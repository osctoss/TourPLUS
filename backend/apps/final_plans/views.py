import decimal
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import FinalPlan
from .serializers import FinalPlanSerializer


class FinalPlanViewSet(viewsets.ModelViewSet):
    serializer_class = FinalPlanSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return FinalPlan.objects.filter(user=self.request.user).select_related(
            'hospital_scenario__hospital_treatment_offering__hospital__city',
            'hospital_scenario__hospital_treatment_offering__treatment_category__specialty',
            'package_match__travel_package__agency'
        ).prefetch_related(
            'destinations__destination__city',
            'hospital_scenario__budget_lines'
        )

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['get'], url_path='export')
    def export_summary(self, request, pk=None):
        """
        Renders a printable and exportable summary of the final medical tourism plan,
        including transparent financial ledger totals, clinical disclosures, and itinerary.
        """
        plan = self.get_object()
        scenario = plan.hospital_scenario
        offering = scenario.hospital_treatment_offering
        hospital = offering.hospital
        package = plan.package_match.travel_package if plan.package_match else None

        # Financial reconciliation
        budget_lines = scenario.budget_lines.all()
        mandatory_total = sum(line.converted_expected_amount for line in budget_lines)
        package_effective_cost = plan.package_match.effective_incremental_cost if plan.package_match else decimal.Decimal('0.00')
        package_credit = plan.package_match.inclusion_credit if plan.package_match else decimal.Decimal('0.00')
        package_listed_price = plan.package_match.listed_package_price if plan.package_match else decimal.Decimal('0.00')

        profile = getattr(plan.user, 'profile', None)
        full_name = f"{profile.first_name} {profile.last_name}".strip() if profile else plan.user.email

        export_data = {
            'plan_id': str(plan.id),
            'plan_title': plan.plan_title,
            'status': plan.status,
            'created_at': plan.created_at.isoformat(),
            'patient': {
                'email': plan.user.email,
                'full_name': full_name or 'Patient',
            },
            'hospital': {
                'name': hospital.name,
                'city': hospital.city.name if hospital.city else '',
                'address': hospital.address,
                'verification_status': hospital.verification_status,
                'international_patient_support': hospital.international_patient_support,
                'website_url': hospital.website_url,
                'treatment_offering': {
                    'category': offering.treatment_category.name,
                    'specialty': offering.treatment_category.specialty.name,
                    'description': offering.offering_description,
                }
            },
            'financial_ledger': {
                'currency': scenario.scenario_currency,
                'mandatory_expenditure': str(mandatory_total),
                'package_listed_price': str(package_listed_price),
                'package_inclusion_credit': str(package_credit),
                'package_effective_incremental_cost': str(package_effective_cost),
                'total_estimated_commitment': str(mandatory_total + package_effective_cost),
                'budget_lines': [
                    {
                        'category': line.expense_category,
                        'category_label': line.get_expense_category_display(),
                        'description': line.description,
                        'expected_amount': str(line.converted_expected_amount),
                        'data_classification': line.data_classification
                    }
                    for line in budget_lines
                ]
            },
            'tourism_itinerary': [
                {
                    'sequence_order': d.sequence_order,
                    'destination_name': d.destination.name,
                    'city': d.destination.city.name if d.destination.city else '',
                    'planned_duration_minutes': d.planned_duration_minutes,
                    'travel_intensity': d.destination.travel_intensity,
                    'planned_visit_date': d.planned_visit_date.isoformat() if d.planned_visit_date else None,
                    'notes': d.notes
                }
                for d in plan.destinations.all()
            ],
            'disclaimers': {
                'medical_safety': (
                    "TourPlus AI is an informational decision-support and planning platform. "
                    "It is NOT a medical provider and does NOT provide medical advice, diagnosis, or treatment. "
                    "All medical treatment must be evaluated and confirmed directly with accredited healthcare professionals."
                ),
                'financial_notice': (
                    "All prices, packages, and cost estimates presented are indicative and subject to change based on actual "
                    "clinical evaluation, seasonal travel fluctuations, and provider confirmation."
                )
            }
        }

        return Response(export_data)
