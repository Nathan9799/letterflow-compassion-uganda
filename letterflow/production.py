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

# Database - Keep it simple for now
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('PGDATABASE', 'railway'),
        'USER': os.environ.get('PGUSER', 'postgres'),
        'PASSWORD': os.environ.get('PGPASSWORD', ''),
        'HOST': os.environ.get('PGHOST', 'localhost'),
        'PORT': os.environ.get('PGPORT', '5432'),
    }
}

# Static files (CSS, JS, Images)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Extra places for collectstatic to find static files.
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Basic security settings (minimal for now)
X_FRAME_OPTIONS = 'DENY'

# Simple logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
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
