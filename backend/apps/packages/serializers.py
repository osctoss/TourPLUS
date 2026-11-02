from rest_framework import serializers
from .models import TravelPackage, PackageDestination, PackageInclusion
from apps.tourism.serializers import TouristDestinationSerializer


class PackageInclusionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PackageInclusion
        fields = [
            'id', 'inclusion_type', 'inclusion_status', 'description',
            'quantity', 'unit', 'service_value_amount',
            'service_value_currency', 'equivalent_budget_category'
        ]


class PackageDestinationSerializer(serializers.ModelSerializer):
    destination = TouristDestinationSerializer(read_only=True)

    class Meta:
        model = PackageDestination
        fields = ['id', 'destination', 'sequence_order', 'planned_visit_duration', 'overnight_stay']


class TravelPackageSerializer(serializers.ModelSerializer):
    agency_name = serializers.CharField(source='agency.name', read_only=True)
    inclusions = PackageInclusionSerializer(many=True, read_only=True)
    package_destinations = PackageDestinationSerializer(many=True, read_only=True)

    class Meta:
        model = TravelPackage
        fields = [
            'id', 'agency', 'agency_name', 'name', 'description',
            'package_type', 'duration_days', 'price_amount',
            'currency', 'price_basis', 'minimum_group_size',
            'maximum_group_size', 'valid_from', 'valid_until',
            'departure_rules', 'cancellation_terms',
            'inclusions', 'package_destinations',
            'verification_status', 'data_classification'
        ]

