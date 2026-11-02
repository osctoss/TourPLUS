from rest_framework import serializers
from .models import FinalPlan, FinalPlanDestination
from apps.tourism.serializers import TouristDestinationSerializer
from apps.recommendations.serializers import HospitalScenarioSerializer, PackageMatchSerializer


class FinalPlanDestinationSerializer(serializers.ModelSerializer):
    destination = TouristDestinationSerializer(read_only=True)
    destination_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = FinalPlanDestination
        fields = ['id', 'destination', 'destination_id', 'sequence_order', 'planned_visit_date', 'planned_duration_minutes', 'notes']


class FinalPlanSerializer(serializers.ModelSerializer):
    hospital_scenario_detail = HospitalScenarioSerializer(source='hospital_scenario', read_only=True)
    package_match_detail = PackageMatchSerializer(source='package_match', read_only=True)
    destinations = FinalPlanDestinationSerializer(many=True, read_only=True)

    class Meta:
        model = FinalPlan
        fields = [
            'id', 'user', 'hospital_scenario', 'hospital_scenario_detail',
            'package_match', 'package_match_detail', 'selected_scope',
            'status', 'plan_title', 'destinations', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

