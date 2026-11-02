#!/usr/bin/env python
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, 'backend')
sys.path.insert(0, BACKEND_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

try:
    import django
    django.setup()
    from apps.geography.models import Country, State, City, ExchangeRate
    from apps.medical.models import Specialty, TreatmentCategory
    from apps.hospitals.models import Hospital, HospitalTreatmentOffering
    from apps.tourism.models import DestinationCategory, TouristDestination
    from apps.agencies.models import TravelAgency
    from apps.packages.models import TravelPackage, PackageInclusion
except ImportError as exc:
    raise ImportError("Failed to initialize Django environment") from exc


def validate():
    print("=" * 60)
    print(" TourPlus AI — Catalogue Integrity Validator")
    print("=" * 60)
    errors = []

    # 1. Geography
    c_count = Country.objects.count()
    s_count = State.objects.count()
    city_count = City.objects.count()
    print(f"[OK] Geography: {c_count} Countries, {s_count} States, {city_count} Cities")
    if city_count < 5:
        errors.append(f"Insufficient cities found: {city_count} (expected >= 5)")

    # 2. Specialties
    specs = list(Specialty.objects.values_list('slug', flat=True))
    print(f"[OK] Specialties: {specs}")
    for req in ['cardiology', 'orthopedics', 'oncology']:
        if req not in specs:
            errors.append(f"Required specialty missing: {req}")

    # 3. Hospitals & Offerings
    h_count = Hospital.objects.count()
    off_count = HospitalTreatmentOffering.objects.count()
    print(f"[OK] Hospitals: {h_count} active hospitals, {off_count} treatment offerings")
    if h_count < 10:
        errors.append(f"Expected at least 10 hospitals, found {h_count}")

    # 4. Tourist Destinations
    d_count = TouristDestination.objects.count()
    cat_count = DestinationCategory.objects.count()
    print(f"[OK] Tourism: {d_count} destinations across {cat_count} categories")
    if d_count < 20:
        errors.append(f"Expected at least 20 destinations, found {d_count}")

    # 5. Travel Packages & Inclusions
    pkg_count = TravelPackage.objects.count()
    inc_count = PackageInclusion.objects.count()
    print(f"[OK] Travel Packages: {pkg_count} packages with {inc_count} inclusions")
    if pkg_count < 3:
        errors.append(f"Expected at least 3 travel packages, found {pkg_count}")

    # 6. Exchange Rates
    fx_count = ExchangeRate.objects.count()
    print(f"[OK] Exchange Rates: {fx_count} rate pairs registered")
    if fx_count < 3:
        errors.append(f"Expected exchange rates for major currencies, found {fx_count}")

    print("-" * 60)
    if errors:
        print(f"FAILED: {len(errors)} validation error(s) found:")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print("SUCCESS: All catalogue invariants passed with zero errors.")
        return True


if __name__ == '__main__':
    success = validate()
    sys.exit(0 if success else 1)
