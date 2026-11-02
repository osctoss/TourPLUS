import decimal
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import TripRequest, TripRequestInterest
from .serializers import TripRequestSerializer
from apps.recommendations.models import RecommendationRun, HospitalScenario
from apps.recommendations.serializers import RecommendationRunSerializer
from engines.hospitals.ranking import HospitalRankingEngine
from engines.budgeting.ledger import BudgetLedgerEngine
from engines.tourism.recommender import TourismRecommendationEngine
from engines.package_matching.matcher import PackageMatchingEngine


class TripRequestViewSet(viewsets.ModelViewSet):
    serializer_class = TripRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Enforce strict patient ownership
        return TripRequest.objects.filter(
            user=self.request.user
        ).select_related('specialty', 'treatment_category').prefetch_related('interests')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], url_path='submit')
    def submit_request(self, request, pk=None):
        trip_request = self.get_object()
        if trip_request.status != TripRequest.Status.DRAFT:
            return Response({'error': 'Only draft requests can be submitted.'}, status=status.HTTP_400_BAD_REQUEST)
        
        trip_request.status = TripRequest.Status.SUBMITTED
        trip_request.submitted_at = timezone.now()
        trip_request.save()
        return Response(TripRequestSerializer(trip_request).data)

    @action(detail=True, methods=['post'], url_path='generate-plan')
    def generate_plan(self, request, pk=None):
        """
        Orchestrates full recommendation generation:
        1. Evaluates and ranks eligible hospitals (MCDM HScore)
        2. Generates deterministic Decimal budget ledger for each scenario
        3. Classifies and recommends recovery-aware tourism destinations across 3 tiers
        4. Matches travel packages and derives Dynamic Inclusion Credit ledger (EPC_p = P_p - I_p)
        """
        trip_request = self.get_object()

        if not trip_request.specialty_id and not trip_request.treatment_category_id:
            return Response(
                {'error': 'A medical specialty or treatment category is required to generate recommendations.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        trip_request.status = TripRequest.Status.PROCESSING
        trip_request.save()

        # Initialize engines
        hospital_engine = HospitalRankingEngine()
        budget_engine = BudgetLedgerEngine()
        tourism_engine = TourismRecommendationEngine()
        package_engine = PackageMatchingEngine()

        # Create immutable RecommendationRun
        run_number = trip_request.recommendation_runs.count() + 1
        rec_run = RecommendationRun.objects.create(
            trip_request=trip_request,
            run_number=run_number,
            status=RecommendationRun.Status.PROCESSING,
            algorithm_version='1.0',
            weight_configuration_snapshot={
                'hospital_ranking': hospital_engine.weights,
                'tourism_ranking': tourism_engine.weights,
                'package_matching': package_engine.weights,
            },
            input_snapshot={
                'specialty_id': str(trip_request.specialty_id) if trip_request.specialty_id else None,
                'treatment_category_id': str(trip_request.treatment_category_id) if trip_request.treatment_category_id else None,
                'budget_amount': str(trip_request.total_budget_amount),
                'budget_currency': trip_request.budget_currency,
                'party_size': trip_request.party_size,
                'available_days': trip_request.available_days,
                'recovery_duration_days': trip_request.recovery_duration_days,
                'travel_intensity': trip_request.travel_intensity_preference,
                'clinician_guidance': trip_request.clinician_travel_guidance_status,
                'interests': [
                    {'category_id': str(i.destination_category_id), 'weight': i.preference_weight}
                    for i in trip_request.interests.all()
                ]
            }
        )

        try:
            # 1. Hospital Ranking & Scenario Generation
            eligible_scenarios, excluded = hospital_engine.evaluate_candidates(
                specialty_id=str(trip_request.specialty_id) if trip_request.specialty_id else None,
                treatment_category_id=str(trip_request.treatment_category_id) if trip_request.treatment_category_id else None,
                total_budget=trip_request.total_budget_amount or decimal.Decimal('0.00'),
            )

            if not eligible_scenarios:
                rec_run.status = RecommendationRun.Status.COMPLETED_WITH_WARNINGS
                rec_run.error_message = "No published hospitals matched the requested medical treatment criteria."
                rec_run.completed_at = timezone.now()
                rec_run.save()
                trip_request.status = TripRequest.Status.COMPLETED
                trip_request.save()
                return Response(RecommendationRunSerializer(rec_run).data, status=status.HTTP_200_OK)

            # Persist scenarios and run downstream engines
            for cand in eligible_scenarios:
                scenario = HospitalScenario.objects.create(
                    recommendation_run=rec_run,
                    hospital_treatment_offering=cand['offering'],
                    rank=cand['rank'],
                    eligibility_status=HospitalScenario.EligibilityStatus.ELIGIBLE,
                    ranking_score=cand['score'],
                    scenario_currency=trip_request.budget_currency or 'USD',
                    scenario_notes=(
                        f"MCDM Hospital Score: {cand['score']:.4f}. "
                        f"Treatment Match: {cand['breakdown']['treatment_match']}, "
                        f"Cost Suitability: {cand['breakdown']['cost_suitability']}, "
                        f"Intl Support: {cand['breakdown']['international_support']}."
                    )
                )

                # 2. Build Budget Ledger
                budget_summary = budget_engine.build_scenario_budget(scenario, trip_request)

                # 3. Recommend Recovery-Aware Tourism (3-Tier)
                tourism_engine.recommend_destinations(
                    scenario=scenario,
                    trip_request=trip_request,
                    discretionary_budget=budget_summary['discretionary_budget']
                )

                # 4. Match Packages & Compute Dynamic Inclusion Credits
                package_engine.match_packages(
                    scenario=scenario,
                    discretionary_budget=budget_summary['discretionary_budget'],
                    party_size=trip_request.party_size
                )

            rec_run.status = RecommendationRun.Status.COMPLETED
            rec_run.completed_at = timezone.now()
            rec_run.save()

            trip_request.status = TripRequest.Status.COMPLETED
            trip_request.save()

            return Response(RecommendationRunSerializer(rec_run).data, status=status.HTTP_201_CREATED)

        except Exception as exc:
            rec_run.status = RecommendationRun.Status.FAILED
            rec_run.error_message = str(exc)
            rec_run.completed_at = timezone.now()
            rec_run.save()
            trip_request.status = TripRequest.Status.FAILED
            trip_request.save()
            return Response(
                {'error': f"Failed to generate recommendation plan: {str(exc)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
