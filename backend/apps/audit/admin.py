from django.contrib import admin
from .models import AuditEvent, RecommendationConfiguration


@admin.register(AuditEvent)
class AuditEventAdmin(admin.ModelAdmin):
    list_display = ('action', 'entity_name', 'entity_id', 'user', 'created_at')
    list_filter = ('action', 'entity_name')
    search_fields = ('entity_name', 'entity_id', 'user__email')
    readonly_fields = ('user', 'action', 'entity_name', 'entity_id', 'change_summary', 'ip_address', 'created_at')


@admin.register(RecommendationConfiguration)
class RecommendationConfigurationAdmin(admin.ModelAdmin):
    list_display = ('version', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)

