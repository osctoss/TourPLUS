import uuid
from django.db import models
from django.utils import timezone
from apps.geography.models import City, DataSource
from apps.hospitals.models import DataClassification, VerificationStatus


class DestinationCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    objects = models.Manager()

    class Meta:
        db_table = 'destination_categories'
        verbose_name_plural = 'Destination Categories'
        ordering = ['name']

    def __str__(self) -> str:
        return str(self.name)


class TouristDestination(models.Model):
    class TravelIntensity(models.TextChoices):
        LOW = 'LOW', 'Low Physical Demand'
        MODERATE = 'MODERATE', 'Moderate Physical Demand'
        HIGH = 'HIGH', 'High Physical Demand'
        UNKNOWN = 'UNKNOWN', 'Unknown'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='destinations')
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    suggested_visit_duration_minutes = models.PositiveIntegerField(default=120)
    travel_intensity = models.CharField(max_length=20, choices=TravelIntensity.choices, default=TravelIntensity.LOW)
    accessibility_notes = models.TextField(blank=True)
    opening_information = models.TextField(blank=True)

    entry_fee_min = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    entry_fee_expected = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    entry_fee_max = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, default='INR')

    categories = models.ManyToManyField(DestinationCategory, through='DestinationCategoryLink', related_name='destinations')

    verification_status = models.CharField(max_length=20, choices=VerificationStatus.choices, default=VerificationStatus.VERIFIED)
    data_classification = models.CharField(max_length=20, choices=DataClassification.choices, default=DataClassification.VERIFIED)
    source = models.ForeignKey(DataSource, on_delete=models.SET_NULL, null=True, blank=True)
    last_verified_at = models.DateTimeField(default=timezone.now)
    is_published = models.BooleanField(default=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = models.Manager()

    class Meta:
        db_table = 'tourist_destinations'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.city.name})"


class DestinationCategoryLink(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    destination = models.ForeignKey(TouristDestination, on_delete=models.CASCADE)
    category = models.ForeignKey(DestinationCategory, on_delete=models.CASCADE)

    objects = models.Manager()

    class Meta:
        db_table = 'destination_category_links'
        unique_together = ('destination', 'category')

    def __str__(self):
        return f"{self.destination.name} - {self.category.name}"


class DestinationCostEstimate(models.Model):
    class CostType(models.TextChoices):
        ENTRY_TICKET = 'ENTRY_TICKET', 'Entry Ticket'
        LOCAL_ACTIVITY = 'LOCAL_ACTIVITY', 'Local Guided Activity'
        LOCAL_TRANSPORT = 'LOCAL_TRANSPORT', 'Local Transit / Taxi'
        FOOD_ESTIMATE = 'FOOD_ESTIMATE', 'Food / Refreshments'
        OTHER = 'OTHER', 'Other Cost'

    class PartyBasis(models.TextChoices):
        PER_PERSON = 'PER_PERSON', 'Per Person'
        PER_GROUP = 'PER_GROUP', 'Per Group'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    destination = models.ForeignKey(TouristDestination, on_delete=models.CASCADE, related_name='cost_estimates')
    cost_type = models.CharField(max_length=30, choices=CostType.choices, default=CostType.ENTRY_TICKET)
    min_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    expected_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    max_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, default='INR')
    party_basis = models.CharField(max_length=20, choices=PartyBasis.choices, default=PartyBasis.PER_PERSON)
    source = models.ForeignKey(DataSource, on_delete=models.SET_NULL, null=True, blank=True)
    data_classification = models.CharField(max_length=20, choices=DataClassification.choices, default=DataClassification.INDICATIVE)

    objects = models.Manager()

    class Meta:
        db_table = 'destination_cost_estimates'
        ordering = ['destination', 'cost_type']

    def __str__(self):
        return f"{self.destination.name} - {self.cost_type} ({self.currency} {self.expected_amount})"

