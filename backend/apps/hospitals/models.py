import uuid
from django.db import models
from django.utils import timezone
from apps.geography.models import City, DataSource
from apps.medical.models import Specialty, TreatmentCategory


class DataClassification(models.TextChoices):
    VERIFIED = 'VERIFIED', 'Verified Provider Data'
    INDICATIVE = 'INDICATIVE', 'Indicative Estimate'
    DEMO = 'DEMO', 'Illustrative Demo Data'
    EXPIRED = 'EXPIRED', 'Expired Record'
    REJECTED = 'REJECTED', 'Rejected'


class VerificationStatus(models.TextChoices):
    VERIFIED = 'VERIFIED', 'Verified'
    PENDING = 'PENDING', 'Pending Verification'
    UNVERIFIED = 'UNVERIFIED', 'Unverified'


class Hospital(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='hospitals')
    address = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    website_url = models.URLField(max_length=500, blank=True)
    
    international_patient_support = models.BooleanField(default=True)
    international_patient_details = models.TextField(blank=True)
    
    verification_status = models.CharField(max_length=20, choices=VerificationStatus.choices, default=VerificationStatus.VERIFIED)
    data_classification = models.CharField(max_length=20, choices=DataClassification.choices, default=DataClassification.VERIFIED)
    source = models.ForeignKey(DataSource, on_delete=models.SET_NULL, null=True, blank=True, related_name='hospitals')
    last_verified_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'hospitals'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.city.name})"


class HospitalSpecialty(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='hospital_specialties')
    specialty = models.ForeignKey(Specialty, on_delete=models.CASCADE, related_name='hospital_links')
    verification_status = models.CharField(max_length=20, choices=VerificationStatus.choices, default=VerificationStatus.VERIFIED)
    source = models.ForeignKey(DataSource, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'hospital_specialties'
        unique_together = ('hospital', 'specialty')
        verbose_name_plural = 'Hospital Specialties'

    def __str__(self):
        return f"{self.hospital.name} - {self.specialty.name}"


class HospitalTreatmentOffering(models.Model):
    class Availability(models.TextChoices):
        AVAILABLE = 'AVAILABLE', 'Available'
        LIMITED = 'LIMITED', 'Limited Availability'
        WAITLIST = 'WAITLIST', 'Waitlist'
        UNAVAILABLE = 'UNAVAILABLE', 'Unavailable'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hospital = models.ForeignKey(Hospital, on_delete=models.CASCADE, related_name='treatment_offerings')
    treatment_category = models.ForeignKey(TreatmentCategory, on_delete=models.CASCADE, related_name='hospital_offerings')
    offering_description = models.TextField(blank=True)
    availability_status = models.CharField(max_length=20, choices=Availability.choices, default=Availability.AVAILABLE)
    verification_status = models.CharField(max_length=20, choices=VerificationStatus.choices, default=VerificationStatus.VERIFIED)
    source = models.ForeignKey(DataSource, on_delete=models.SET_NULL, null=True, blank=True)
    last_verified_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'hospital_treatment_offerings'
        unique_together = ('hospital', 'treatment_category')
        verbose_name_plural = 'Hospital Treatment Offerings'

    def __str__(self):
        return f"{self.hospital.name} - {self.treatment_category.name}"


class TreatmentCostEstimate(models.Model):
    class PriceBasis(models.TextChoices):
        PER_PROCEDURE = 'PER_PROCEDURE', 'Per Procedure / Treatment'
        PACKAGE = 'PACKAGE', 'Comprehensive Medical Package'
        PER_DAY = 'PER_DAY', 'Per Inpatient Day'
        INDICATIVE_RANGE = 'INDICATIVE_RANGE', 'Indicative Cost Range'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hospital_treatment_offering = models.OneToOneField(HospitalTreatmentOffering, on_delete=models.CASCADE, related_name='cost_estimate')
    min_amount = models.DecimalField(max_digits=12, decimal_places=2)
    expected_amount = models.DecimalField(max_digits=12, decimal_places=2)
    max_amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    price_basis = models.CharField(max_length=30, choices=PriceBasis.choices, default=PriceBasis.INDICATIVE_RANGE)
    included_services = models.TextField(blank=True, help_text="e.g. Surgeon fee, OT charges, 5 days ward stay")
    excluded_services = models.TextField(blank=True, help_text="e.g. Special implants, extended ICU, companion meals")
    valid_from = models.DateField(default=timezone.now)
    valid_until = models.DateField(null=True, blank=True)
    source = models.ForeignKey(DataSource, on_delete=models.SET_NULL, null=True, blank=True)
    data_classification = models.CharField(max_length=20, choices=DataClassification.choices, default=DataClassification.INDICATIVE)
    last_verified_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'treatment_cost_estimates'
        verbose_name = 'Treatment Cost Estimate'
        verbose_name_plural = 'Treatment Cost Estimates'

    def __str__(self):
        return f"{self.hospital_treatment_offering} ({self.currency} {self.expected_amount})"

