from django.contrib import admin
from .models import DestinationCategory, TouristDestination, DestinationCategoryLink, DestinationCostEstimate


class DestinationCategoryLinkInline(admin.TabularInline):
    model = DestinationCategoryLink
    extra = 1


class DestinationCostEstimateInline(admin.TabularInline):
    model = DestinationCostEstimate
    extra = 1


@admin.register(DestinationCategory)
class DestinationCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(TouristDestination)
class TouristDestinationAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'travel_intensity', 'entry_fee_expected', 'currency', 'verification_status', 'is_published')
    search_fields = ('name', 'city__name')
    list_filter = ('travel_intensity', 'verification_status', 'data_classification', 'is_published', 'city__state')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [DestinationCategoryLinkInline, DestinationCostEstimateInline]

