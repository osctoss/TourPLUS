"""
Production Settings for TourPlus AI
"""

import os
from urllib.parse import urlparse, parse_qs
from .base import *  # noqa: F401, F403

DEBUG = False

ALLOWED_HOSTS = [h.strip() for h in os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',') if h.strip()]

# Database Configuration (Supabase / PostgreSQL with SSL)
database_url = os.environ.get('DATABASE_URL')
if database_url and ('postgres' in database_url or 'psql' in database_url):
    url = urlparse(database_url)
    db_options = {'sslmode': 'require'}
    if url.query:
        qs = parse_qs(url.query)
        if 'sslmode' in qs:
            db_options['sslmode'] = qs['sslmode'][0]

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': url.path[1:] if url.path else 'postgres',
            'USER': url.username or 'postgres',
            'PASSWORD': url.password or '',
            'HOST': url.hostname or 'localhost',
            'PORT': str(url.port or 5432),
            'OPTIONS': db_options,
        }
    }
else:
    raise ValueError("Production requires a valid PostgreSQL/Supabase DATABASE_URL environment variable.")

# Security Hardening
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
