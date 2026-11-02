import decimal
from typing import List, Dict, Any
from apps.recommendations.models import HospitalScenario, DestinationRecommendation
from apps.trip_planning.models import TripRequest
from apps.tourism.models import TouristDestination
from apps.hospitals.models import VerificationStatus
from integrations.maps.routes import RouteEngine
from integrations.exchange_rates.converter import CurrencyConverter


class TourismRecommendationEngine:
    """
    Recovery-Aware 3-Tier Tourism Engine.
    Recommends feasible tourist destinations classified into:
      1. LOCAL_REGIONAL (nearby hospital city)
      2. STATE_LEVEL (within hospital's Indian state)
      3. NATIONAL (other Indian states)
    Enforces medical recovery constraint boundaries and flags destinations for clinical review.
    """

    def __init__(self, weights: Dict[str, float] = None):
        self.weights = weights or {
            'interest': 0.40,
            'geography': 0.25,
            'cost': 0.20,
            'confidence': 0.15
        }

    def recommend_destinations(
        self,
        scenario: HospitalScenario,
        trip_request: TripRequest,
        discretionary_budget: decimal.Decimal
    ) -> List[DestinationRecommendation]:
        """
        Evaluates published destinations and persists top recommendations for each scope.
        """
        # Clear existing recommendations for idempotency
        scenario.destinations.all().delete()

        hospital = scenario.hospital_treatment_offering.hospital
        hospital_city = hospital.city
        hospital_state = hospital_city.state if hospital_city else None

        user_interests = {
            str(i.destination_category_id): i.preference_weight
            for i in trip_request.interests.all()
        }

        all_destinations = TouristDestination.objects.filter(
            is_published=True
        ).select_related('city', 'city__state').prefetch_related('categories')

        scored_candidates: List[Dict[str, Any]] = []

        for dest in all_destinations:
            # 1. Geographic Distance & 3-Tier Scope Classification
            dist_km, duration_mins = RouteEngine.estimate_route(
                float(hospital.latitude) if hospital.latitude else None,
                float(hospital.longitude) if hospital.longitude else None,
                float(dest.latitude) if dest.latitude else None,
                float(dest.longitude) if dest.longitude else None,
            )

            is_same_city = (dest.city_id == hospital_city.id) if hospital_city else False
            is_same_state = (dest.city and dest.city.state_id == hospital_state.id) if (dest.city and hospital_state) else False

            if is_same_city or dist_km <= 100.0:
                scope = DestinationRecommendation.Scope.LOCAL_REGIONAL
                g_score = max(0.6, 1.0 - (dist_km / 200.0))
            elif is_same_state or dist_km <= 350.0:
                scope = DestinationRecommendation.Scope.STATE_LEVEL
                g_score = max(0.4, 0.85 - (dist_km / 500.0))
            else:
                scope = DestinationRecommendation.Scope.NATIONAL
                g_score = max(0.2, 0.65 - (dist_km / 2500.0))

            # 2. Medical Recovery & Clinical Guidance Boundary
            needs_clinical_review = (
                trip_request.clinician_travel_guidance_status == TripRequest.ClinicianGuidance.NOT_PROVIDED
            )

            # High intensity sightseeing during early recovery needs clinician clearance
            if trip_request.travel_intensity_preference == TripRequest.TravelIntensity.LOW and dest.travel_intensity == TouristDestination.TravelIntensity.HIGH:
                needs_clinical_review = True

            if needs_clinical_review:
                feasibility = DestinationRecommendation.Feasibility.REQUIRES_CLINICAL_REVIEW
                recovery_status = 'REQUIRES_CLINICIAN_CONFIRMATION'
                explanation = "Post-treatment transit & activity requires confirmed guidance by treating physician."
            else:
                feasibility = DestinationRecommendation.Feasibility.FEASIBLE
                recovery_status = 'CLINICALLY_PERMITTED'
                explanation = f"Comfortable post-procedure activity matching {trip_request.get_travel_intensity_preference_display().lower()} intensity."

            # 3. Interest Matching Score (I_s)
            dest_category_ids = [str(cat.id) for cat in dest.categories.all()]
            if user_interests and dest_category_ids:
                matched_weights = [user_interests[cid] for cid in dest_category_ids if cid in user_interests]
                if matched_weights:
                    i_score = max(matched_weights) / 5.0
                else:
                    i_score = 0.50
            else:
                i_score = 0.70  # Baseline neutral score

            # 4. Cost Suitability Score (C_s)
            entry_fee = dest.entry_fee_expected or decimal.Decimal('0.00')
            target_curr = scenario.scenario_currency or 'USD'
            converted_entry_fee = CurrencyConverter.convert(entry_fee, dest.currency, target_curr)
            
            # Transit cost approximation
            transit_cost = decimal.Decimal(str(round(dist_km * 0.40, 2)))
            converted_transit = CurrencyConverter.convert(transit_cost, 'USD', target_curr)
            total_dest_cost = converted_entry_fee + converted_transit

            if discretionary_budget > 0:
                cost_ratio = float(total_dest_cost / discretionary_budget)
                c_score = max(0.2, min(1.0, 1.0 - (cost_ratio * 0.5)))
            else:
                c_score = 0.3

            # 5. Data Completeness & Verification (V_s)
            v_score = 1.0 if dest.verification_status == VerificationStatus.VERIFIED else 0.75

            # Composite Destination Score
            w = self.weights
            d_score = (
                w['interest'] * i_score +
                w['geography'] * g_score +
                w['cost'] * c_score +
                w['confidence'] * v_score
            )

            scored_candidates.append({
                'destination': dest,
                'tourism_scope': scope,
                'interest_score': decimal.Decimal(str(round(i_score, 4))),
                'geography_score': decimal.Decimal(str(round(g_score, 4))),
                'cost_score': decimal.Decimal(str(round(c_score, 4))),
                'data_confidence_score': decimal.Decimal(str(round(v_score, 4))),
                'recovery_review_status': recovery_status,
                'estimated_visit_cost': converted_entry_fee,
                'estimated_route_cost': converted_transit,
                'estimated_route_duration': duration_mins,
                'feasibility_status': feasibility,
                'explanation': explanation,
                'composite_score': d_score
            })

        # Group and rank by scope
        recommendations_to_create = []
        for scope in [
            DestinationRecommendation.Scope.LOCAL_REGIONAL,
            DestinationRecommendation.Scope.STATE_LEVEL,
            DestinationRecommendation.Scope.NATIONAL
        ]:
            scope_items = [c for c in scored_candidates if c['tourism_scope'] == scope]
            scope_items.sort(key=lambda x: x['composite_score'], reverse=True)

            for rank_idx, item in enumerate(scope_items[:5], start=1):
                recommendations_to_create.append(DestinationRecommendation(
                    hospital_scenario=scenario,
                    destination=item['destination'],
                    tourism_scope=item['tourism_scope'],
                    rank=rank_idx,
                    interest_score=item['interest_score'],
                    geography_score=item['geography_score'],
                    cost_score=item['cost_score'],
                    data_confidence_score=item['data_confidence_score'],
                    recovery_review_status=item['recovery_review_status'],
                    estimated_visit_cost=item['estimated_visit_cost'],
                    estimated_route_cost=item['estimated_route_cost'],
                    estimated_route_duration=item['estimated_route_duration'],
                    feasibility_status=item['feasibility_status'],
                    explanation=item['explanation']
                ))

        created = DestinationRecommendation.objects.bulk_create(recommendations_to_create)
        return created
