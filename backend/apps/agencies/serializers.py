from rest_framework import serializers
from .models import TravelAgency


class TravelAgencySerializer(serializers.ModelSerializer):
    headquarters_city_name = serializers.CharField(source='headquarters_city.name', read_only=True)

    class Meta:
        model = TravelAgency
        fields = [
            'id', 'name', 'slug', 'website_url', 'contact_email',
            'contact_phone', 'headquarters_city_name',
            'verification_status', 'data_classification'
        ]

