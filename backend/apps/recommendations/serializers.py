from rest_framework import serializers
from .models import (
    RecommendationRun,
    HospitalScenario,
    ScenarioBudgetLine,
    DestinationRecommendation,
    PackageMatch,
    PackageMatchInclusionCredit
)
from apps.hospitals.serializers import HospitalTreatmentOfferingSerializer
from apps.tourism.serializers import TouristDestinationSerializer
from apps.packages.serializers import TravelPackageSerializer


class ScenarioBudgetLineSerializer(serializers.ModelSerializer):
    class Meta:
        model = ScenarioBudgetLine
        fields = [
            'id', 'expense_category', 'description', 'min_amount',
            'expected_amount', 'max_amount', 'source_currency',
            'scenario_currency', 'exchange_rate_snapshot',
            'converted_expected_amount', 'quantity', 'unit',
            'data_classification'
        ]


class DestinationRecommendationSerializer(serializers.ModelSerializer):
    destination = TouristDestinationSerializer(read_only=True)

    class Meta:
        model = DestinationRecommendation
        fields = [
            'id', 'destination', 'tourism_scope', 'rank',
            'interest_score', 'geography_score', 'cost_score',
            'data_confidence_score', 'recovery_review_status',
            'estimated_visit_cost', 'estimated_route_cost',
            'estimated_route_duration', 'feasibility_status',
            'explanation'
        ]


class PackageMatchInclusionCreditSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageMatchInclusionCredit
        fields = ['id', 'package_inclusion', 'scenario_budget_line', 'credited_amount', 'credited_currency', 'credit_reason']


class PackageMatchSerializer(serializers.ModelSerializer):
    travel_package = TravelPackageSerializer(read_only=True)
    credits = PackageMatchInclusionCreditSerializer(many=True, read_only=True)

    class Meta:
        model = PackageMatch
        fields = [
            'id', 'travel_package', 'rank', 'destination_coverage_score',
            'inclusion_credit', 'listed_package_price',
            'effective_incremental_cost', 'remaining_discretionary_budget',
            'budget_feasibility_status', 'itinerary_fit_score',
            'agency_reliability_score', 'overall_score', 'explanation',
            'credits'
        ]


class HospitalScenarioSerializer(serializers.ModelSerializer):
    hospital_offering = HospitalTreatmentOfferingSerializer(source='hospital_treatment_offering', read_only=True)
    budget_lines = ScenarioBudgetLineSerializer(many=True, read_only=True)

    class Meta:
        model = HospitalScenario
        fields = [
            'id', 'hospital_offering', 'rank', 'eligibility_status',
            'exclusion_reason', 'ranking_score', 'scenario_currency',
            'scenario_notes', 'budget_lines'
        ]


class RecommendationRunSerializer(serializers.ModelSerializer):
    scenarios = HospitalScenarioSerializer(many=True, read_only=True)

    class Meta:
        model = RecommendationRun
        fields = [
            'id', 'trip_request', 'run_number', 'status',
            'algorithm_version', 'started_at', 'completed_at',
            'scenarios'
        ]

