from rest_framework import serializers
from .models import DestinationCategory, TouristDestination, DestinationCostEstimate


class DestinationCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = DestinationCategory
        fields = ['id', 'name', 'slug', 'description']


class DestinationCostEstimateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DestinationCostEstimate
        fields = ['id', 'cost_type', 'min_amount', 'expected_amount', 'max_amount', 'currency', 'party_basis']


class TouristDestinationSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city.name', read_only=True)
    state_name = serializers.CharField(source='city.state.name', read_only=True)
    categories = DestinationCategorySerializer(many=True, read_only=True)
    cost_estimates = DestinationCostEstimateSerializer(many=True, read_only=True)

    class Meta:
        model = TouristDestination
        fields = [
            'id', 'name', 'slug', 'description', 'city_name',
            'state_name', 'latitude', 'longitude',
            'suggested_visit_duration_minutes', 'travel_intensity',
            'accessibility_notes', 'opening_information',
            'entry_fee_min', 'entry_fee_expected', 'entry_fee_max',
            'currency', 'categories', 'cost_estimates',
            'verification_status', 'data_classification'
        ]

