from rest_framework import serializers
from .models import Hospital, HospitalTreatmentOffering, TreatmentCostEstimate
from apps.geography.serializers import CitySerializer


class TreatmentCostEstimateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TreatmentCostEstimate
        fields = [
            'id', 'min_amount', 'expected_amount', 'max_amount',
            'currency', 'price_basis', 'included_services',
            'excluded_services', 'data_classification', 'last_verified_at'
        ]


class HospitalTreatmentOfferingSerializer(serializers.ModelSerializer):
    treatment_category_name = serializers.CharField(source='treatment_category.name', read_only=True)
    specialty_name = serializers.CharField(source='treatment_category.specialty.name', read_only=True)
    cost_estimate = TreatmentCostEstimateSerializer(read_only=True)

    class Meta:
        model = HospitalTreatmentOffering
        fields = [
            'id', 'treatment_category', 'treatment_category_name',
            'specialty_name', 'offering_description',
            'availability_status', 'verification_status', 'cost_estimate'
        ]


class HospitalListSerializer(serializers.ModelSerializer):
    city_name = serializers.CharField(source='city.name', read_only=True)
    state_name = serializers.CharField(source='city.state.name', read_only=True)

    class Meta:
        model = Hospital
        fields = [
            'id', 'name', 'slug', 'city_name', 'state_name',
            'international_patient_support', 'verification_status',
            'data_classification'
        ]


class HospitalDetailSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)
    treatment_offerings = HospitalTreatmentOfferingSerializer(many=True, read_only=True)

    class Meta:
        model = Hospital
        fields = [
            'id', 'name', 'slug', 'description', 'city', 'address',
            'postal_code', 'latitude', 'longitude', 'website_url',
            'international_patient_support', 'international_patient_details',
            'verification_status', 'data_classification', 'last_verified_at',
            'treatment_offerings'
        ]

