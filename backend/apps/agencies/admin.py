from django.contrib import admin
from .models import TravelAgency


@admin.register(TravelAgency)
class TravelAgencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'headquarters_city', 'contact_email', 'verification_status', 'is_published')
    search_fields = ('name', 'headquarters_city__name')
    list_filter = ('verification_status', 'data_classification', 'is_published')
    prepopulated_fields = {'slug': ('name',)}

