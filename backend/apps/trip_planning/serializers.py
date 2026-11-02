from rest_framework import serializers
from .models import TripRequest, TripRequestInterest
from apps.tourism.serializers import DestinationCategorySerializer


class TripRequestInterestSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='destination_category.name', read_only=True)

    class Meta:
        model = TripRequestInterest
        fields = ['id', 'destination_category', 'category_name', 'preference_weight']


class TripRequestInterestWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripRequestInterest
        fields = ['destination_category', 'preference_weight']


class TripRequestSerializer(serializers.ModelSerializer):
    interests = TripRequestInterestSerializer(many=True, read_only=True)
    interests_input = TripRequestInterestWriteSerializer(many=True, required=False, write_only=True)
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
            'status', 'interests', 'interests_input', 'created_at', 'updated_at', 'submitted_at'
        ]
        read_only_fields = ['id', 'user', 'status', 'created_at', 'updated_at', 'submitted_at']

    def create(self, validated_data):
        interests_data = validated_data.pop('interests_input', None)
        user = self.context['request'].user
        validated_data['user'] = user
        instance = super().create(validated_data)
        if interests_data:
            for item in interests_data:
                TripRequestInterest.objects.create(trip_request=instance, **item)
        return instance

    def update(self, instance, validated_data):
        interests_data = validated_data.pop('interests_input', None)
        instance = super().update(instance, validated_data)
        if interests_data is not None:
            instance.interests.all().delete()
            for item in interests_data:
                TripRequestInterest.objects.create(trip_request=instance, **item)
        return instance

