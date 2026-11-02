import uuid
from django.db import models


class Specialty(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()

    class Meta:
        db_table = 'specialties'
        verbose_name_plural = 'Specialties'
        ordering = ['name']

    def __str__(self):
        return self.name


class TreatmentCategory(models.Model):
    class ReviewStatus(models.TextChoices):
        VERIFIED = 'VERIFIED', 'Clinically Verified'
        INDICATIVE = 'INDICATIVE', 'Indicative'
        PENDING_REVIEW = 'PENDING_REVIEW', 'Pending Review'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, related_name='treatment_categories')
    name = models.CharField(max_length=150)
    slug = models.SlugField(max_length=150)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    review_status = models.CharField(max_length=30, choices=ReviewStatus.choices, default=ReviewStatus.VERIFIED)

    objects = models.Manager()

    class Meta:
        db_table = 'treatment_categories'
        unique_together = ('specialty', 'name')
        verbose_name_plural = 'Treatment Categories'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.specialty.name})"

