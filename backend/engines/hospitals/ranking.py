import decimal
from typing import List, Dict, Any, Tuple, Optional
from apps.hospitals.models import Hospital, HospitalTreatmentOffering, VerificationStatus


class HospitalRankingEngine:
    """
    Two-stage recommendation engine for hospitals:
    1. Hard Constraints Filtering:
       - Published & active
       - Offers matching verified specialty and treatment category
       - Has valid location and cost data
    2. Soft Ranking (MCDM):
       HScore = 0.45*T + 0.20*C + 0.15*I + 0.10*G + 0.10*V
    """

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = weights or {
            'treatment_match': 0.45,
            'cost_suitability': 0.20,
            'international_support': 0.15,
            'geography': 0.10,
            'data_completeness': 0.10
        }

    def evaluate_candidates(
        self,
        specialty_id: Optional[str] = None,
        treatment_category_id: Optional[str] = None,
        total_budget: decimal.Decimal = decimal.Decimal('0.00'),
        preferred_city_id: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        """
        Returns (eligible_ranked_scenarios, excluded_candidates)
        """
        all_hospitals = Hospital.objects.filter(is_published=True).select_related(
            'city', 'city__state'
        ).prefetch_related(
            'treatment_offerings__treatment_category',
            'treatment_offerings__cost_estimate'
        )

        eligible_scenarios = []
        excluded = []

        for hospital in all_hospitals:
            # 1. Hard Filter: Treatment category offering
            offerings = hospital.treatment_offerings.filter(
                availability_status__in=[
                    HospitalTreatmentOffering.Availability.AVAILABLE,
                    HospitalTreatmentOffering.Availability.LIMITED
                ]
            )

            if treatment_category_id:
                matched_offering = offerings.filter(treatment_category_id=treatment_category_id).first()
            elif specialty_id:
                matched_offering = offerings.filter(treatment_category__specialty_id=specialty_id).first()
            else:
                matched_offering = None

            if not matched_offering:
                excluded.append({
                    'hospital': hospital,
                    'reason': 'Hospital does not offer the requested verified treatment category.'
                })
                continue

            cost_estimate = getattr(matched_offering, 'cost_estimate', None)
            if not cost_estimate:
                excluded.append({
                    'hospital': hospital,
                    'reason': 'No verified or indicative cost schedule available for this offering.'
                })
                continue

            # 2. Soft Criteria Scores (Normalized 0.0 - 1.0)
            # T: Treatment Offering Match (1.0 if exact category match)
            t_score = 1.0 if (treatment_category_id and str(matched_offering.treatment_category_id) == treatment_category_id) else 0.85

            # C: Cost Suitability (rewards affordability within budget)
            c_score = 0.5
            if total_budget > 0:
                expected_cost = cost_estimate.expected_amount
                if expected_cost <= total_budget:
                    # Normalized suitability
                    c_score = min(1.0, max(0.1, float(decimal.Decimal('1.0') - (expected_cost / total_budget) * decimal.Decimal('0.5'))))
                else:
                    c_score = 0.1  # Significant penalty if procedure exceeds total budget

            # I: International Patient Support
            i_score = 1.0 if hospital.international_patient_support else 0.2

            # G: Geographic Suitability
            g_score = 0.8
            if preferred_city_id and str(hospital.city_id) == preferred_city_id:
                g_score = 1.0

            # V: Verification and Completeness
            v_score = 1.0 if hospital.verification_status == VerificationStatus.VERIFIED else 0.7

            # Composite HScore
            w = self.weights
            h_score = (
                w['treatment_match'] * t_score +
                w['cost_suitability'] * c_score +
                w['international_support'] * i_score +
                w['geography'] * g_score +
                w['data_completeness'] * v_score
            )

            eligible_scenarios.append({
                'hospital': hospital,
                'offering': matched_offering,
                'cost_estimate': cost_estimate,
                'score': decimal.Decimal(str(round(h_score, 4))),
                'breakdown': {
                    'treatment_match': t_score,
                    'cost_suitability': c_score,
                    'international_support': i_score,
                    'geography': g_score,
                    'data_completeness': v_score,
                }
            })

        # Sort descending by score
        eligible_scenarios.sort(key=lambda x: x['score'], reverse=True)

        # Assign ranks
        for rank_idx, scenario in enumerate(eligible_scenarios, start=1):
            scenario['rank'] = rank_idx

        return eligible_scenarios, excluded
