"""
Development Settings for TourPlus AI
"""

import os
from urllib.parse import urlparse
from .base import *

DEBUG = True

# Database Configuration
database_url = os.environ.get('DATABASE_URL')
if database_url and 'postgres' in database_url:
    url = urlparse(database_url)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': url.path[1:] if url.path else 'tourplus_db',
            'USER': url.username or '',
            'PASSWORD': url.password or '',
            'HOST': url.hostname or 'localhost',
            'PORT': str(url.port or 5432),
        }
    }
elif os.environ.get('POSTGRES_DB') and os.environ.get('USE_POSTGRES') == 'True':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB', 'tourplus_db'),
            'USER': os.environ.get('POSTGRES_USER', 'tourplus_user'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'tourplus_password'),
            'HOST': os.environ.get('POSTGRES_HOST', 'localhost'),
            'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        }
    }
else:
    # Development default: SQLite for fast standalone local tests without external DB dependencies
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
