from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, PatientProfile, ConsentRecord


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'role', 'is_active', 'is_staff', 'created_at')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('email',)
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Permissions', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'email_verified_at', 'created_at')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'role', 'password', 'is_staff', 'is_superuser'),
        }),
    )
    readonly_fields = ('created_at', 'last_login')


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'origin_country_code', 'display_currency', 'created_at')
    search_fields = ('user__email', 'full_name', 'origin_country_code')
    list_filter = ('display_currency', 'preferred_language')


@admin.register(ConsentRecord)
class ConsentRecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'consent_type', 'policy_version', 'accepted_at', 'source')
    search_fields = ('user__email', 'consent_type')
    list_filter = ('consent_type', 'policy_version')

