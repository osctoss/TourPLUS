from django.contrib import admin
from .models import TripRequest, TripRequestInterest


class TripRequestInterestInline(admin.TabularInline):
    model = TripRequestInterest
    extra = 1


@admin.register(TripRequest)
class TripRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'specialty', 'total_budget_amount', 'budget_currency', 'party_size', 'status', 'created_at')
    list_filter = ('status', 'specialty', 'budget_currency', 'clinician_travel_guidance_status')
    search_fields = ('user__email', 'known_condition_text')
    inlines = [TripRequestInterestInline]

