from rest_framework import serializers
from .models import FinalPlan, FinalPlanDestination
from apps.tourism.serializers import TouristDestinationSerializer
from apps.recommendations.serializers import HospitalScenarioSerializer, PackageMatchSerializer


class FinalPlanDestinationWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinalPlanDestination
        fields = ['destination', 'sequence_order', 'planned_visit_date', 'planned_duration_minutes', 'notes']


class FinalPlanDestinationSerializer(serializers.ModelSerializer):
    destination = TouristDestinationSerializer(read_only=True)

    class Meta:
        model = FinalPlanDestination
        fields = ['id', 'destination', 'sequence_order', 'planned_visit_date', 'planned_duration_minutes', 'notes']


class FinalPlanSerializer(serializers.ModelSerializer):
    hospital_scenario_detail = HospitalScenarioSerializer(source='hospital_scenario', read_only=True)
    package_match_detail = PackageMatchSerializer(source='package_match', read_only=True)
    destinations = FinalPlanDestinationSerializer(many=True, read_only=True)
    destinations_input = FinalPlanDestinationWriteSerializer(many=True, required=False, write_only=True)

    class Meta:
        model = FinalPlan
        fields = [
            'id', 'user', 'hospital_scenario', 'hospital_scenario_detail',
            'package_match', 'package_match_detail', 'selected_scope',
            'status', 'plan_title', 'destinations', 'destinations_input', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def create(self, validated_data):
        destinations_data = validated_data.pop('destinations_input', None)
        validated_data['user'] = self.context['request'].user
        plan = super().create(validated_data)
        if destinations_data:
            for item in destinations_data:
                FinalPlanDestination.objects.create(final_plan=plan, **item)
        return plan
