import uuid
from django.db import models
from django.utils import timezone
from django.conf import settings
from apps.geography.models import Country
from apps.medical.models import Specialty, TreatmentCategory
from apps.tourism.models import DestinationCategory


class TripRequest(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft Assessment'
        SUBMITTED = 'SUBMITTED', 'Submitted for Recommendation'
        PROCESSING = 'PROCESSING', 'Processing Recommendations'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Processing Failed'
        ARCHIVED = 'ARCHIVED', 'Archived'

    class ClinicianGuidance(models.TextChoices):
        PROVIDED = 'PROVIDED', 'Clinician Guidance Provided'
        NOT_PROVIDED = 'NOT_PROVIDED', 'Not Yet Provided / Requires Clinician Confirmation'

    class TravelIntensity(models.TextChoices):
        LOW = 'LOW', 'Low Intensity / Gentle Walking'
        MODERATE = 'MODERATE', 'Moderate Intensity'
        HIGH = 'HIGH', 'High / Active Sightseeing'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='trip_requests')
    origin_country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True, blank=True)
    
    specialty = models.ForeignKey(Specialty, on_delete=models.SET_NULL, null=True, blank=True)
    treatment_category = models.ForeignKey(TreatmentCategory, on_delete=models.SET_NULL, null=True, blank=True)
    known_condition_text = models.TextField(blank=True, help_text="Patient-provided medical condition notes")

    total_budget_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    budget_currency = models.CharField(max_length=3, default='USD')
    party_size = models.PositiveIntegerField(default=1)

    preferred_arrival_date = models.DateField(null=True, blank=True)
    preferred_departure_date = models.DateField(null=True, blank=True)
    available_days = models.PositiveIntegerField(default=14)
    recovery_duration_days = models.PositiveIntegerField(null=True, blank=True)

    clinician_travel_guidance_status = models.CharField(
        max_length=30,
        choices=ClinicianGuidance.choices,
        default=ClinicianGuidance.NOT_PROVIDED
    )
    clinician_restrictions = models.JSONField(default=list, blank=True)
    insurance_status = models.CharField(max_length=100, blank=True)
    travel_intensity_preference = models.CharField(
        max_length=20,
        choices=TravelIntensity.choices,
        default=TravelIntensity.LOW
    )

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'trip_requests'
        ordering = ['-created_at']

    def __str__(self):
        return f"Trip Request {self.id} ({self.user.email}) - {self.status}"


class TripRequestInterest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trip_request = models.ForeignKey(TripRequest, on_delete=models.CASCADE, related_name='interests')
    destination_category = models.ForeignKey(DestinationCategory, on_delete=models.CASCADE)
    preference_weight = models.PositiveSmallIntegerField(default=3, help_text="Weight from 1 to 5")

    class Meta:
        db_table = 'trip_request_interests'
        unique_together = ('trip_request', 'destination_category')

    def __str__(self):
        return f"{self.destination_category.name} (Weight: {self.preference_weight})"

