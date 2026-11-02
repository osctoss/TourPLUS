import uuid
from django.db import models
from django.utils import timezone
from apps.agencies.models import TravelAgency
from apps.tourism.models import TouristDestination
from apps.geography.models import DataSource
from apps.hospitals.models import DataClassification, VerificationStatus


class TravelPackage(models.Model):
    class PackageType(models.TextChoices):
        LOCAL = 'LOCAL', 'Local / Regional'
        STATE = 'STATE', 'State-Level'
        NATIONAL = 'NATIONAL', 'National / Pan-India'
        CUSTOM = 'CUSTOM', 'Customized Itinerary'

    class PriceBasis(models.TextChoices):
        PER_PERSON = 'PER_PERSON', 'Per Person'
        PER_GROUP = 'PER_GROUP', 'Per Group / Private Tour'
        PER_ROOM = 'PER_ROOM', 'Per Room'

    class Availability(models.TextChoices):
        AVAILABLE = 'AVAILABLE', 'Available'
        LIMITED = 'LIMITED', 'Limited Slots'
        ON_REQUEST = 'ON_REQUEST', 'On Request'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agency = models.ForeignKey(TravelAgency, on_delete=models.CASCADE, related_name='packages')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    package_type = models.CharField(max_length=20, choices=PackageType.choices, default=PackageType.LOCAL)
    duration_days = models.PositiveIntegerField(default=3)
    
    price_amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='USD')
    price_basis = models.CharField(max_length=20, choices=PriceBasis.choices, default=PriceBasis.PER_PERSON)
    minimum_group_size = models.PositiveIntegerField(default=1)
    maximum_group_size = models.PositiveIntegerField(default=10)

    valid_from = models.DateField(default=timezone.now)
    valid_until = models.DateField(null=True, blank=True)
    departure_rules = models.TextField(blank=True)
    cancellation_terms = models.TextField(blank=True)

    destinations = models.ManyToManyField(TouristDestination, through='PackageDestination', related_name='packages')

    availability_status = models.CharField(max_length=20, choices=Availability.choices, default=Availability.AVAILABLE)
    verification_status = models.CharField(max_length=20, choices=VerificationStatus.choices, default=VerificationStatus.VERIFIED)
    data_classification = models.CharField(max_length=20, choices=DataClassification.choices, default=DataClassification.VERIFIED)
    source = models.ForeignKey(DataSource, on_delete=models.SET_NULL, null=True, blank=True)
    last_verified_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        db_table = 'travel_packages'
        verbose_name = 'Travel Package'
        verbose_name_plural = 'Travel Packages'
        ordering = ['agency', 'name']

    def __str__(self):
        return f"{self.name} ({self.agency.name}) - {self.currency} {self.price_amount}"


class PackageDestination(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    package = models.ForeignKey(TravelPackage, on_delete=models.CASCADE, related_name='package_destinations')
    destination = models.ForeignKey(TouristDestination, on_delete=models.CASCADE, related_name='destination_packages')
    sequence_order = models.PositiveIntegerField(default=1)
    planned_visit_duration = models.PositiveIntegerField(default=120, help_text="Duration in minutes")
    overnight_stay = models.BooleanField(default=False)

    objects = models.Manager()

    class Meta:
        db_table = 'package_destinations'
        unique_together = ('package', 'destination')
        ordering = ['package', 'sequence_order']

    def __str__(self):
        return f"{self.package.name} -> {self.sequence_order}. {self.destination.name}"


class PackageInclusion(models.Model):
    class Status(models.TextChoices):
        INCLUDED = 'INCLUDED', 'Included in Base Price'
        OPTIONAL_EXTRA = 'OPTIONAL_EXTRA', 'Optional Add-on'
        NOT_INCLUDED = 'NOT_INCLUDED', 'Explicitly Excluded'

    class EquivalentCategory(models.TextChoices):
        INTERNATIONAL_FLIGHT = 'INTERNATIONAL_FLIGHT', 'International Flight'
        ACCOMMODATION = 'ACCOMMODATION', 'Hotel / Accommodation'
        LOCAL_TRANSPORT = 'LOCAL_TRANSPORT', 'Local Transport / Airport Transfers'
        VISA = 'VISA', 'Visa Processing Service'
        MISCELLANEOUS = 'MISCELLANEOUS', 'Miscellaneous Service'
        NONE = 'NONE', 'None (Standard Tourism / Sightseeing / Meals)'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    package = models.ForeignKey(TravelPackage, on_delete=models.CASCADE, related_name='inclusions')
    inclusion_type = models.CharField(max_length=100, help_text="e.g. Airport Transfer, 3-Star Hotel Stay, Guided City Tour")
    inclusion_status = models.CharField(max_length=20, choices=Status.choices, default=Status.INCLUDED)
    description = models.TextField(blank=True)
    quantity = models.DecimalField(max_digits=8, decimal_places=2, default=1.0, help_text="e.g. 3 nights, 2 transfers")
    unit = models.CharField(max_length=50, blank=True, help_text="e.g. nights, trips, tickets")
    
    service_value_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, help_text="Comparable standalone value for credit")
    service_value_currency = models.CharField(max_length=3, default='USD')
    
    equivalent_budget_category = models.CharField(
        max_length=30,
        choices=EquivalentCategory.choices,
        default=EquivalentCategory.NONE,
        help_text="Original mandatory expense this inclusion credits/replaces"
    )

    verification_status = models.CharField(max_length=20, choices=VerificationStatus.choices, default=VerificationStatus.VERIFIED)

    objects = models.Manager()

    class Meta:
        db_table = 'package_inclusions'
        verbose_name = 'Package Inclusion'
        verbose_name_plural = 'Package Inclusions'

    def __str__(self):
        return f"{self.package.name} - {self.inclusion_type} ({self.equivalent_budget_category})"

