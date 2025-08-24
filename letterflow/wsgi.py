"""
WSGI config for letterflow project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Only use production settings if we're actually on Railway
# Check for Railway-specific environment variables
if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('PGHOST'):
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'letterflow.production')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'letterflow.settings')

application = get_wsgi_application()
