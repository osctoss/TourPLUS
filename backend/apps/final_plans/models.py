import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings
from apps.recommendations.models import HospitalScenario, PackageMatch
from apps.tourism.models import TouristDestination


class FinalPlan(models.Model):
    class Status(models.TextChoices):
        SAVED = 'SAVED', 'Saved'
        CONFIRMED = 'CONFIRMED', 'Confirmed with Providers'
        ARCHIVED = 'ARCHIVED', 'Archived'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='final_plans')
    hospital_scenario = models.ForeignKey(HospitalScenario, on_delete=models.CASCADE)
    package_match = models.ForeignKey(PackageMatch, on_delete=models.SET_NULL, null=True, blank=True)
    selected_scope = models.CharField(max_length=20, default='LOCAL_REGIONAL')
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SAVED)
    plan_title = models.CharField(max_length=255, default='My Medical Tourism Plan')

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        db_table = 'final_plans'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.plan_title} ({self.user.email})"


class FinalPlanDestination(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    final_plan = models.ForeignKey(FinalPlan, on_delete=models.CASCADE, related_name='destinations')
    destination = models.ForeignKey(TouristDestination, on_delete=models.CASCADE)
    sequence_order = models.PositiveIntegerField(default=1)
    planned_visit_date = models.DateField(null=True, blank=True)
    planned_duration_minutes = models.PositiveIntegerField(default=120)
    notes = models.TextField(blank=True)

    objects = models.Manager()

    class Meta:
        db_table = 'final_plan_destinations'
        ordering = ['final_plan', 'sequence_order']

    def __str__(self):
        return f"{self.final_plan.plan_title} - Stop #{self.sequence_order}: {self.destination.name}"

