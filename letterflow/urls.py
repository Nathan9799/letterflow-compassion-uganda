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
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
import os

@csrf_exempt
def healthcheck(request):
    """Simple healthcheck endpoint for Railway - no CSRF required"""
    try:
        # Get actual database info
        from django.db import connection
        db_engine = connection.settings_dict.get('ENGINE', 'unknown')
        db_host = connection.settings_dict.get('HOST', 'unknown')
        db_name = connection.settings_dict.get('NAME', 'unknown')
        
        # Determine database type
        if 'postgresql' in db_engine:
            db_type = f"PostgreSQL ({db_host}:{db_name})"
        elif 'sqlite' in db_engine:
            db_type = "SQLite"
        else:
            db_type = "Unknown"
        
        return HttpResponse(
            f"OK - Django {os.environ.get('DJANGO_SETTINGS_MODULE', 'unknown')} - "
            f"Database: {db_type}",
            content_type="text/plain"
        )
    except Exception as e:
        # Even if Django fails, return something
        return HttpResponse(f"OK - Basic response", content_type="text/plain")

@csrf_exempt
def db_test(request):
    """Test database connection and show table info"""
    try:
        from django.db import connection
        from django.db import connection
        cursor = connection.cursor()
        
        # Test basic connection
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
        
        # Check if auth tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'auth_%'
            ORDER BY table_name;
        """)
        auth_tables = cursor.fetchall()
        
        # Check if our app tables exist
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'shipping_%'
            ORDER BY table_name;
        """)
        shipping_tables = cursor.fetchall()
        
        response_text = f"""
Database Test Results:
====================
Database Version: {db_version[0] if db_version else 'Unknown'}

Auth Tables Found:
{chr(10).join([f"- {table[0]}" for table in auth_tables])}

Shipping Tables Found:
{chr(10).join([f"- {table[0]}" for table in shipping_tables])}

Connection Status: SUCCESS
        """
        
        return HttpResponse(response_text, content_type="text/plain")
        
    except Exception as e:
        return HttpResponse(f"Database Test Failed: {str(e)}", content_type="text/plain")

def test_endpoint(request):
    """Simple test endpoint to verify the app is responding"""
    return HttpResponse("Test endpoint working!", content_type="text/plain")

def root_redirect(request):
    """Redirect root URL to the login page for security"""
    # Force logout any existing session to ensure clean state
    if request.user.is_authenticated:
        logout(request)
    return redirect('login')

def debug_auth(request):
    """Debug endpoint to see authentication state"""
    auth_info = f"""
Authentication Debug Info:
========================
User: {request.user}
Is Authenticated: {request.user.is_authenticated}
Session ID: {request.session.session_key}
User ID: {request.user.id if request.user.is_authenticated else 'None'}
Username: {request.user.username if request.user.is_authenticated else 'None'}
    """
    return HttpResponse(auth_info, content_type="text/plain")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),  # Built-in auth (login, logout, etc.)
    path('accounts/', include('accounts.urls')),  # Custom password change views
    path('shipping/', include('shipping.urls')),
    path('db-test/', db_test),  # Database test endpoint
    path('test/', test_endpoint),  # Test endpoint
    path('health/', healthcheck),  # Healthcheck at /health/
    path('debug-auth/', debug_auth),  # Debug authentication state
    path('', root_redirect),  # Root URL redirects to login
]
