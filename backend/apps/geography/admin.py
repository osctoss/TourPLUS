from django.contrib import admin
from .models import Country, State, City, DataSource, ExchangeRate


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('name', 'iso2', 'iso3', 'default_currency', 'is_active')
    search_fields = ('name', 'iso2', 'iso3')
    list_filter = ('is_active', 'default_currency')


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'country')
    search_fields = ('name', 'code', 'country__name')
    list_filter = ('country',)


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ('name', 'state', 'latitude', 'longitude', 'is_active')
    search_fields = ('name', 'state__name')
    list_filter = ('is_active', 'state__country')


@admin.register(DataSource)
class DataSourceAdmin(admin.ModelAdmin):
    list_display = ('source_name', 'publisher', 'reliability_level', 'accessed_at')
    search_fields = ('source_name', 'publisher')
    list_filter = ('reliability_level',)


@admin.register(ExchangeRate)
class ExchangeRateAdmin(admin.ModelAdmin):
    list_display = ('base_currency', 'quote_currency', 'rate', 'effective_at', 'provider_name')
    search_fields = ('base_currency', 'quote_currency')
    list_filter = ('base_currency', 'quote_currency')

