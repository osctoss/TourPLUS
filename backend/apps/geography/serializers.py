from rest_framework import serializers
from .models import Country, State, City


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'name', 'iso2', 'iso3', 'default_currency']


class StateSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', read_only=True)

    class Meta:
        model = State
        fields = ['id', 'country', 'country_name', 'name', 'code']


class CitySerializer(serializers.ModelSerializer):
    state_name = serializers.CharField(source='state.name', read_only=True)
    country_name = serializers.CharField(source='state.country.name', read_only=True)

    class Meta:
        model = City
        fields = ['id', 'state', 'state_name', 'country_name', 'name', 'latitude', 'longitude']

