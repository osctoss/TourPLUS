import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings


class AuditEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=100)
    entity_name = models.CharField(max_length=100)
    entity_id = models.CharField(max_length=100, blank=True)
    change_summary = models.JSONField(default=dict)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'audit_events'
        ordering = ['-created_at']

    def __str__(self):
        user_str = self.user.email if self.user else "System"
        return f"[{self.created_at.strftime('%Y-%m-%d %H:%M')}] {user_str} -> {self.action} on {self.entity_name} ({self.entity_id})"


class RecommendationConfiguration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    version = models.CharField(max_length=20, unique=True, default='1.0')
    is_active = models.BooleanField(default=True)
    weights = models.JSONField(default=dict, help_text="Configurable weights for Hospital, Tourism, and Package ranking")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'recommendation_configurations'
        ordering = ['-created_at']

    def __str__(self):
        return f"Config v{self.version} ({'Active' if self.is_active else 'Inactive'})"

