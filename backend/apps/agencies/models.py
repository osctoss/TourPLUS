import uuid
from django.db import models
from django.utils import timezone
from apps.geography.models import City, DataSource
from apps.hospitals.models import DataClassification, VerificationStatus


class TravelAgency(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    website_url = models.URLField(max_length=500, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=50, blank=True)
    headquarters_city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True, blank=True, related_name='agencies')
    
    verification_status = models.CharField(max_length=20, choices=VerificationStatus.choices, default=VerificationStatus.VERIFIED)
    data_classification = models.CharField(max_length=20, choices=DataClassification.choices, default=DataClassification.VERIFIED)
    source = models.ForeignKey(DataSource, on_delete=models.SET_NULL, null=True, blank=True)
    last_verified_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        db_table = 'travel_agencies'
        verbose_name_plural = 'Travel Agencies'
        ordering = ['name']

    def __str__(self) -> str:
        return str(self.name)

