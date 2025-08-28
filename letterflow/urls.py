"""
URL configuration for letterflow project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
import os

def healthcheck(request):
    """Simple healthcheck endpoint for Railway - no database access"""
    try:
        # Just return basic info without touching database
        return HttpResponse(
            f"OK - Django {os.environ.get('DJANGO_SETTINGS_MODULE', 'unknown')} - "
            f"Database: {'PostgreSQL' if os.environ.get('PGHOST') else 'SQLite'}",
            content_type="text/plain"
        )
    except Exception as e:
        # Even if Django fails, return something
        return HttpResponse(f"OK - Basic response", content_type="text/plain")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # Built-in auth (login, logout, etc.)
    path('accounts/', include('accounts.urls')),  # Custom password change views
    path('shipping/', include('shipping.urls')),
    path('', healthcheck),  # Healthcheck at root
]
