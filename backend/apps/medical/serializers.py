from rest_framework import serializers
from .models import Specialty, TreatmentCategory


class TreatmentCategorySerializer(serializers.ModelSerializer):
    specialty_name = serializers.CharField(source='specialty.name', read_only=True)

    class Meta:
        model = TreatmentCategory
        fields = ['id', 'specialty', 'specialty_name', 'name', 'slug', 'description', 'review_status']


class SpecialtySerializer(serializers.ModelSerializer):
    treatment_categories = TreatmentCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Specialty
        fields = ['id', 'name', 'slug', 'description', 'treatment_categories']

