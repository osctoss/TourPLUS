import uuid
from django.db import models
from django.utils import timezone


class Country(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    iso2 = models.CharField(max_length=2, unique=True)
    iso3 = models.CharField(max_length=3, unique=True)
    default_currency = models.CharField(max_length=3, default='USD')
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'countries'
        verbose_name_plural = 'Countries'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.iso2})"


class State(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='states')
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=10)

    class Meta:
        db_table = 'states'
        unique_together = ('country', 'name')
        ordering = ['name']

    def __str__(self):
        return f"{self.name}, {self.country.iso2}"


class City(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    state = models.ForeignKey(State, on_delete=models.CASCADE, related_name='cities')
    name = models.CharField(max_length=100)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'cities'
        unique_together = ('state', 'name')
        verbose_name_plural = 'Cities'
        ordering = ['name']

    def __str__(self):
        return f"{self.name}, {self.state.name}"


class DataSource(models.Model):
    class Reliability(models.TextChoices):
        AUTHORITATIVE = 'AUTHORITATIVE', 'Authoritative Source'
        PROVIDER_PUBLISHED = 'PROVIDER_PUBLISHED', 'Provider Published'
        THIRD_PARTY_ESTIMATE = 'THIRD_PARTY_ESTIMATE', 'Third-Party Estimate'
        UNVERIFIED = 'UNVERIFIED', 'Unverified'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source_name = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255, blank=True)
    source_url = models.URLField(max_length=500, blank=True)
    source_type = models.CharField(max_length=50, blank=True)
    reliability_level = models.CharField(max_length=30, choices=Reliability.choices, default=Reliability.PROVIDER_PUBLISHED)
    accessed_at = models.DateTimeField(default=timezone.now)
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'data_sources'
        verbose_name = 'Data Source'
        verbose_name_plural = 'Data Sources'

    def __str__(self):
        return f"{self.source_name} ({self.reliability_level})"


class ExchangeRate(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    base_currency = models.CharField(max_length=3)
    quote_currency = models.CharField(max_length=3)
    rate = models.DecimalField(max_digits=12, decimal_places=6)
    effective_at = models.DateTimeField(default=timezone.now)
    provider_name = models.CharField(max_length=100, default='Curated')
    source_url = models.URLField(max_length=500, blank=True)

    class Meta:
        db_table = 'exchange_rates'
        verbose_name = 'Exchange Rate'
        verbose_name_plural = 'Exchange Rates'
        ordering = ['-effective_at']

    def __str__(self):
        return f"1 {self.base_currency} = {self.rate} {self.quote_currency} ({self.effective_at.date()})"

