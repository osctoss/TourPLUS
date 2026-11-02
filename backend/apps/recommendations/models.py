import uuid
from django.db import models
from django.utils import timezone
from apps.trip_planning.models import TripRequest
from apps.hospitals.models import HospitalTreatmentOffering, DataClassification
from apps.tourism.models import TouristDestination
from apps.packages.models import TravelPackage, PackageInclusion


class RecommendationRun(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        PROCESSING = 'PROCESSING', 'Processing'
        COMPLETED = 'COMPLETED', 'Completed'
        COMPLETED_WITH_WARNINGS = 'COMPLETED_WITH_WARNINGS', 'Completed With Warnings'
        FAILED = 'FAILED', 'Failed'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    trip_request = models.ForeignKey(TripRequest, on_delete=models.CASCADE, related_name='recommendation_runs')
    run_number = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=30, choices=Status.choices, default=Status.PENDING)
    algorithm_version = models.CharField(max_length=20, default='1.0')
    weight_configuration_snapshot = models.JSONField(default=dict)
    input_snapshot = models.JSONField(default=dict)
    started_at = models.DateTimeField(default=timezone.now)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    objects = models.Manager()

    class Meta:
        db_table = 'recommendation_runs'
        ordering = ['-started_at']

    def __str__(self):
        return f"Run #{self.run_number} for Request {self.trip_request_id} ({self.status})"


class HospitalScenario(models.Model):
    class EligibilityStatus(models.TextChoices):
        ELIGIBLE = 'ELIGIBLE', 'Eligible'
        INELIGIBLE = 'INELIGIBLE', 'Ineligible'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recommendation_run = models.ForeignKey(RecommendationRun, on_delete=models.CASCADE, related_name='scenarios')
    hospital_treatment_offering = models.ForeignKey(HospitalTreatmentOffering, on_delete=models.CASCADE)
    rank = models.PositiveIntegerField(default=1)
    eligibility_status = models.CharField(max_length=20, choices=EligibilityStatus.choices, default=EligibilityStatus.ELIGIBLE)
    exclusion_reason = models.TextField(blank=True)
    ranking_score = models.DecimalField(max_digits=5, decimal_places=4, default=0.0000)
    scenario_currency = models.CharField(max_length=3, default='USD')
    scenario_notes = models.TextField(blank=True)

    objects = models.Manager()
    budget_lines: models.Manager = None  # type: ignore
    destinations: models.Manager = None  # type: ignore
    package_matches: models.Manager = None  # type: ignore

    class Meta:
        db_table = 'hospital_scenarios'
        ordering = ['rank', '-ranking_score']

    def __str__(self):
        return f"Scenario {self.id}: {self.hospital_treatment_offering.hospital.name} (Rank #{self.rank})"


class ScenarioBudgetLine(models.Model):
    class ExpenseCategory(models.TextChoices):
        TREATMENT = 'TREATMENT', 'Medical Treatment / Procedure'
        INTERNATIONAL_FLIGHT = 'INTERNATIONAL_FLIGHT', 'International Flights'
        ACCOMMODATION = 'ACCOMMODATION', 'Hotel / Lodging Stay'
        VISA = 'VISA', 'Medical Visa & Processing'
        LOCAL_TRANSPORT = 'LOCAL_TRANSPORT', 'Local Transfers & Transit'
        MISCELLANEOUS = 'MISCELLANEOUS', 'Contingency / Miscellaneous'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hospital_scenario = models.ForeignKey(HospitalScenario, on_delete=models.CASCADE, related_name='budget_lines')
    expense_category = models.CharField(max_length=30, choices=ExpenseCategory.choices)
    description = models.CharField(max_length=255)
    
    min_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    expected_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    max_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    source_currency = models.CharField(max_length=3, default='USD')

    scenario_currency = models.CharField(max_length=3, default='USD')
    exchange_rate_snapshot = models.DecimalField(max_digits=12, decimal_places=6, default=1.000000)
    converted_expected_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)

    quantity = models.DecimalField(max_digits=8, decimal_places=2, default=1.00)
    unit = models.CharField(max_length=50, blank=True)
    data_classification = models.CharField(max_length=20, choices=DataClassification.choices, default=DataClassification.INDICATIVE)

    objects = models.Manager()

    class Meta:
        db_table = 'scenario_budget_lines'
        ordering = ['hospital_scenario', 'expense_category']

    def __str__(self):
        return f"{self.expense_category}: {self.scenario_currency} {self.converted_expected_amount}"


class DestinationRecommendation(models.Model):
    class Scope(models.TextChoices):
        LOCAL_REGIONAL = 'LOCAL_REGIONAL', 'Local / Regional'
        STATE_LEVEL = 'STATE_LEVEL', 'State-Level'
        NATIONAL = 'NATIONAL', 'National / Pan-India'

    class Feasibility(models.TextChoices):
        FEASIBLE = 'FEASIBLE', 'Feasible'
        REQUIRES_CLINICAL_REVIEW = 'REQUIRES_CLINICAL_REVIEW', 'Requires Clinical Confirmation'
        INFEASIBLE = 'INFEASIBLE', 'Infeasible'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hospital_scenario = models.ForeignKey(HospitalScenario, on_delete=models.CASCADE, related_name='destinations')
    destination = models.ForeignKey(TouristDestination, on_delete=models.CASCADE)
    tourism_scope = models.CharField(max_length=20, choices=Scope.choices, default=Scope.LOCAL_REGIONAL)
    rank = models.PositiveIntegerField(default=1)

    interest_score = models.DecimalField(max_digits=5, decimal_places=4, default=0.0000)
    geography_score = models.DecimalField(max_digits=5, decimal_places=4, default=0.0000)
    cost_score = models.DecimalField(max_digits=5, decimal_places=4, default=0.0000)
    data_confidence_score = models.DecimalField(max_digits=5, decimal_places=4, default=0.0000)
    
    recovery_review_status = models.CharField(max_length=30, default='CONFIRMED')
    estimated_visit_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    estimated_route_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    estimated_route_duration = models.PositiveIntegerField(default=0, help_text="Duration in minutes")
    feasibility_status = models.CharField(max_length=30, choices=Feasibility.choices, default=Feasibility.FEASIBLE)
    explanation = models.TextField(blank=True)

    objects = models.Manager()

    class Meta:
        db_table = 'destination_recommendations'
        ordering = ['hospital_scenario', 'tourism_scope', 'rank']

    def __str__(self):
        return f"{self.destination.name} ({self.tourism_scope} - Rank #{self.rank})"


class PackageMatch(models.Model):
    class Feasibility(models.TextChoices):
        FEASIBLE = 'FEASIBLE', 'Within Budget'
        OVER_BUDGET = 'OVER_BUDGET', 'Exceeds Discretionary Budget'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    hospital_scenario = models.ForeignKey(HospitalScenario, on_delete=models.CASCADE, related_name='package_matches')
    travel_package = models.ForeignKey(TravelPackage, on_delete=models.CASCADE)
    rank = models.PositiveIntegerField(default=1)

    destination_coverage_score = models.DecimalField(max_digits=5, decimal_places=4, default=0.0000)
    inclusion_credit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    listed_package_price = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    effective_incremental_cost = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    remaining_discretionary_budget = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    budget_feasibility_status = models.CharField(max_length=20, choices=Feasibility.choices, default=Feasibility.FEASIBLE)

    itinerary_fit_score = models.DecimalField(max_digits=5, decimal_places=4, default=0.0000)
    agency_reliability_score = models.DecimalField(max_digits=5, decimal_places=4, default=0.0000)
    overall_score = models.DecimalField(max_digits=5, decimal_places=4, default=0.0000)
    explanation = models.TextField(blank=True)

    objects = models.Manager()

    class Meta:
        db_table = 'package_matches'
        ordering = ['hospital_scenario', 'rank']

    def __str__(self):
        return f"Package Match: {self.travel_package.name} (Effective Cost: {self.effective_incremental_cost})"


class PackageMatchInclusionCredit(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    package_match = models.ForeignKey(PackageMatch, on_delete=models.CASCADE, related_name='credits')
    package_inclusion = models.ForeignKey(PackageInclusion, on_delete=models.CASCADE)
    scenario_budget_line = models.ForeignKey(ScenarioBudgetLine, on_delete=models.CASCADE)
    credited_amount = models.DecimalField(max_digits=12, decimal_places=2)
    credited_currency = models.CharField(max_length=3, default='USD')
    credit_reason = models.TextField(blank=True)

    objects = models.Manager()

    class Meta:
        db_table = 'package_match_inclusion_credits'

    def __str__(self):
        return f"Credit of {self.credited_currency} {self.credited_amount} on {self.scenario_budget_line.expense_category}"

