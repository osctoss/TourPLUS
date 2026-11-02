from django.contrib import admin
from .models import FinalPlan, FinalPlanDestination


class FinalPlanDestinationInline(admin.TabularInline):
    model = FinalPlanDestination
    extra = 1


@admin.register(FinalPlan)
class FinalPlanAdmin(admin.ModelAdmin):
    list_display = ('plan_title', 'user', 'hospital_scenario', 'selected_scope', 'status', 'created_at')
    search_fields = ('plan_title', 'user__email')
    list_filter = ('status', 'selected_scope')
    inlines = [FinalPlanDestinationInline]

