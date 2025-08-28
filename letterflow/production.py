"""
Production settings for Railway deployment
"""
import os
import dj_database_url
from pathlib import Path
from .settings import *

print("=== PRODUCTION SETTINGS LOADING ===")
print(f"Current working directory: {os.getcwd()}")
print(f"Environment variables: {dict(os.environ)}")

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-in-production')

# Railway provides the PORT environment variable
ALLOWED_HOSTS = ["*"]  # Safe for testing as you suggested

# Add your custom domain if you have one
if os.environ.get('CUSTOM_DOMAIN'):
    ALLOWED_HOSTS.append(os.environ.get('CUSTOM_DOMAIN'))

# Railway-specific settings
RAILWAY_ENVIRONMENT = os.environ.get('RAILWAY_ENVIRONMENT', 'development')
RAILWAY_PORT = os.environ.get('PORT', '8000')

print(f"Railway Environment: {RAILWAY_ENVIRONMENT}")
print(f"Railway Port: {RAILWAY_PORT}")
print(f"Allowed Hosts: {ALLOWED_HOSTS}")

# Database - Use dj-database-url as you suggested (much better approach)
print("Setting up database...")
DATABASES = {
    "default": dj_database_url.config(
        default=os.getenv("DATABASE_URL"),
        conn_max_age=600,
        ssl_require=True
    )
}

print(f"Database configured: {DATABASES['default']['ENGINE']}")
print(f"Database host: {DATABASES['default'].get('HOST', 'N/A')}")
print(f"Database name: {DATABASES['default'].get('NAME', 'N/A')}")

# Static files (CSS, JS, Images) - Railway optimized
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# Only include STATICFILES_DIRS if you *actually* have a static/ folder in project root
STATICFILES_DIRS = []
if (BASE_DIR / 'static').exists():
    STATICFILES_DIRS.append(BASE_DIR / 'static')

print(f"Static root: {STATIC_ROOT}")
print(f"Static files dirs: {STATICFILES_DIRS}")

# WhiteNoise configuration for serving static files
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Add WhiteNoise to existing middleware (don't override)
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")

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

# CSRF and Security settings for Railway
CSRF_TRUSTED_ORIGINS = [
    'https://web-production-40fc9.up.railway.app',
    'https://*.up.railway.app',
    'https://*.railway.app',
]

# HTTPS settings
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = False  # Set to True if you want to force HTTPS
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

print("=== PRODUCTION SETTINGS LOADED SUCCESSFULLY ===")
