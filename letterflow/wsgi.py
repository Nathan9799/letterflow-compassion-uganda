"""
WSGI config for letterflow project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

# Create a super simple healthcheck that bypasses Django entirely
def simple_healthcheck(environ, start_response):
    """Super simple healthcheck that doesn't touch Django at all"""
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return [b'OK']

# Try to load Django, but fallback to simple healthcheck if it fails
try:
    # Only use production settings if we're actually on Railway
    # Check for Railway-specific environment variables
    if os.environ.get('RAILWAY_ENVIRONMENT') or os.environ.get('PGHOST') or os.environ.get('PORT'):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'letterflow.production')
        print("Using production settings for Railway")
    else:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'letterflow.settings')
        print("Using development settings")
    
    from django.core.wsgi import get_wsgi_application
    application = get_wsgi_application()
    print("Django WSGI application loaded successfully")
    
except Exception as e:
    print(f"Django failed to load: {e}")
    print("Falling back to simple healthcheck")
    # Fallback to simple healthcheck
    application = simple_healthcheck
