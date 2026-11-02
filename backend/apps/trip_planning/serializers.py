from rest_framework import serializers
from .models import TripRequest, TripRequestInterest
from apps.tourism.serializers import DestinationCategorySerializer


class TripRequestInterestSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='destination_category.name', read_only=True)

    class Meta:
        model = TripRequestInterest
        fields = ['id', 'destination_category', 'category_name', 'preference_weight']


class TripRequestSerializer(serializers.ModelSerializer):
    interests = TripRequestInterestSerializer(many=True, read_only=True)
    specialty_name = serializers.CharField(source='specialty.name', read_only=True)
    treatment_category_name = serializers.CharField(source='treatment_category.name', read_only=True)

    class Meta:
        model = TripRequest
        fields = [
            'id', 'user', 'origin_country', 'specialty', 'specialty_name',
            'treatment_category', 'treatment_category_name',
            'known_condition_text', 'total_budget_amount', 'budget_currency',
            'party_size', 'preferred_arrival_date', 'preferred_departure_date',
            'available_days', 'recovery_duration_days',
            'clinician_travel_guidance_status', 'clinician_restrictions',
            'insurance_status', 'travel_intensity_preference',
            'status', 'interests', 'created_at', 'updated_at', 'submitted_at'
        ]
        read_only_fields = ['id', 'user', 'status', 'created_at', 'updated_at', 'submitted_at']

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)

