from django.contrib import admin
from .models import Specialty, TreatmentCategory


@admin.register(Specialty)
class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_active')
    search_fields = ('name', 'slug')
    list_filter = ('is_active',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(TreatmentCategory)
class TreatmentCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'specialty', 'review_status', 'is_active')
    search_fields = ('name', 'specialty__name')
    list_filter = ('specialty', 'review_status', 'is_active')
    prepopulated_fields = {'slug': ('name',)}

