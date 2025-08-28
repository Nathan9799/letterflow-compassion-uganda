"""
Production settings for Railway deployment
"""
import os
from pathlib import Path
from .settings import *

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-in-production')

# Railway provides the PORT environment variable
ALLOWED_HOSTS = [
    os.environ.get('RAILWAY_STATIC_URL', 'localhost'),
    os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'localhost'),
    'localhost',
    '127.0.0.1',
    '0.0.0.0',
    '*',  # Allow all hosts temporarily for debugging
]

# Add your custom domain if you have one
if os.environ.get('CUSTOM_DOMAIN'):
    ALLOWED_HOSTS.append(os.environ.get('CUSTOM_DOMAIN'))

# Database - Check if we have Railway database variables
# Use SQLite by default to avoid database connection issues during startup
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Only try PostgreSQL if we're sure we have all the variables
if all([
    os.environ.get('PGDATABASE'),
    os.environ.get('PGUSER'),
    os.environ.get('PGPASSWORD'),
    os.environ.get('PGHOST'),
    os.environ.get('PGPORT')
]):
    try:
        # Test if we can actually connect to PostgreSQL
        import psycopg
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': os.environ.get('PGDATABASE'),
                'USER': os.environ.get('PGUSER'),
                'PASSWORD': os.environ.get('PGPASSWORD'),
                'HOST': os.environ.get('PGHOST'),
                'PORT': os.environ.get('PGPORT'),
            }
        }
        print("Using PostgreSQL database")
    except Exception as e:
        print(f"PostgreSQL connection failed, using SQLite: {e}")
        # Keep SQLite if PostgreSQL fails
else:
    print("Using SQLite database (no PostgreSQL environment variables)")

# Static files (CSS, JS, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Extra places for collectstatic to find static files - only if they exist
STATICFILES_DIRS = []
if (BASE_DIR / 'static').exists():
    STATICFILES_DIRS.append(BASE_DIR / 'static')

# Basic security settings (minimal for now)
X_FRAME_OPTIONS = 'DENY'

# Simple logging with more detail
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# Simple cache
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@yourdomain.com')

# Session configuration
SESSION_COOKIE_AGE = 3600  # 1 hour
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# Disable database operations during startup to prevent crashes
DATABASE_CONNECTION_MAX_AGE = 0
