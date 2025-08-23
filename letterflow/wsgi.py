"""
WSGI config for letterflow project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

# Use production settings if DJANGO_SETTINGS_MODULE is not set
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'letterflow.production')

application = get_wsgi_application()
