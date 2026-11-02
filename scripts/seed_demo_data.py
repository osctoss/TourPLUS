#!/usr/bin/env python
import os
import sys

# Ensure backend is on PYTHONPATH
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_DIR = os.path.join(BASE_DIR, 'backend')
sys.path.insert(0, BACKEND_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')

try:
    import django
    from django.core.management import call_command
    django.setup()
except ImportError as exc:
    raise ImportError(
        "Couldn't import Django. Are you sure it's installed and available on your PYTHONPATH environment variable?"
    ) from exc


def main():
    print("TourPlus AI: Seeding Curated Medical & Tourism Catalogue...")
    call_command('seed_catalogue')
    print("TourPlus AI: Seeding completed successfully.")


if __name__ == '__main__':
    main()
