from django.contrib import admin
from .models import (
    RecommendationRun,
    HospitalScenario,
    ScenarioBudgetLine,
    DestinationRecommendation,
    PackageMatch,
    PackageMatchInclusionCredit
)


class ScenarioBudgetLineInline(admin.TabularInline):
    model = ScenarioBudgetLine
    extra = 0


class DestinationRecommendationInline(admin.TabularInline):
    model = DestinationRecommendation
    extra = 0


class PackageMatchInline(admin.TabularInline):
    model = PackageMatch
    extra = 0


@admin.register(RecommendationRun)
class RecommendationRunAdmin(admin.ModelAdmin):
    list_display = ('id', 'trip_request', 'run_number', 'status', 'algorithm_version', 'started_at', 'completed_at')
    list_filter = ('status', 'algorithm_version')


@admin.register(HospitalScenario)
class HospitalScenarioAdmin(admin.ModelAdmin):
    list_display = ('id', 'recommendation_run', 'hospital_treatment_offering', 'rank', 'ranking_score', 'eligibility_status')
    list_filter = ('eligibility_status', 'scenario_currency')
    inlines = [ScenarioBudgetLineInline, DestinationRecommendationInline, PackageMatchInline]


@admin.register(PackageMatchInclusionCredit)
class PackageMatchInclusionCreditAdmin(admin.ModelAdmin):
    list_display = ('id', 'package_match', 'package_inclusion', 'credited_amount', 'credited_currency')

