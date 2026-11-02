from django.contrib import admin
from .models import Hospital, HospitalSpecialty, HospitalTreatmentOffering, TreatmentCostEstimate


class HospitalSpecialtyInline(admin.TabularInline):
    model = HospitalSpecialty
    extra = 1


class TreatmentCostEstimateInline(admin.StackedInline):
    model = TreatmentCostEstimate
    extra = 0


@admin.register(Hospital)
class HospitalAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'verification_status', 'data_classification', 'international_patient_support', 'is_published')
    search_fields = ('name', 'city__name')
    list_filter = ('verification_status', 'data_classification', 'is_published', 'city__state')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [HospitalSpecialtyInline]


@admin.register(HospitalTreatmentOffering)
class HospitalTreatmentOfferingAdmin(admin.ModelAdmin):
    list_display = ('hospital', 'treatment_category', 'availability_status', 'verification_status')
    search_fields = ('hospital__name', 'treatment_category__name')
    list_filter = ('availability_status', 'verification_status', 'treatment_category__specialty')
    inlines = [TreatmentCostEstimateInline]


@admin.register(TreatmentCostEstimate)
class TreatmentCostEstimateAdmin(admin.ModelAdmin):
    list_display = ('hospital_treatment_offering', 'min_amount', 'expected_amount', 'max_amount', 'currency', 'data_classification')
    search_fields = ('hospital_treatment_offering__hospital__name', 'hospital_treatment_offering__treatment_category__name')
    list_filter = ('currency', 'data_classification')

