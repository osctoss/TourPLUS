from django.contrib import admin
from .models import TravelPackage, PackageDestination, PackageInclusion


class PackageDestinationInline(admin.TabularInline):
    model = PackageDestination
    extra = 1


class PackageInclusionInline(admin.TabularInline):
    model = PackageInclusion
    extra = 1


@admin.register(TravelPackage)
class TravelPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'agency', 'package_type', 'duration_days', 'price_amount', 'currency', 'price_basis', 'verification_status', 'is_published')
    search_fields = ('name', 'agency__name')
    list_filter = ('package_type', 'price_basis', 'verification_status', 'data_classification', 'is_published')
    inlines = [PackageDestinationInline, PackageInclusionInline]

