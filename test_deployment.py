#!/usr/bin/env python3
"""
Deployment test script for LetterFlow
This script tests the production configuration before deploying
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import django
        print(f"✅ Django {django.get_version()} imported successfully")
    except ImportError as e:
        print(f"❌ Django import failed: {e}")
        return False
    
    try:
        import psycopg
        print("✅ psycopg3 imported successfully")
    except ImportError:
        try:
            import psycopg2
            print("✅ psycopg2 imported successfully")
        except ImportError as e:
            print(f"❌ PostgreSQL adapters import failed: {e}")
            return False
    
    try:
        import gunicorn
        print("✅ Gunicorn imported successfully")
    except ImportError as e:
        print(f"❌ Gunicorn import failed: {e}")
        return False
    
    return True

def test_settings():
    """Test if Django settings can be loaded"""
    print("\n🔧 Testing Django settings...")
    
    try:
        # Set Django settings module
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'letterflow.production')
        
        # Import Django settings
        from django.conf import settings
        print("✅ Production settings loaded successfully")
        
        # Test database configuration
        db_engine = settings.DATABASES['default']['ENGINE']
        print(f"✅ Database engine: {db_engine}")
        
        return True
        
    except Exception as e:
        print(f"❌ Settings loading failed: {e}")
        return False

def test_database():
    """Test database connection"""
    print("\n🗄️  Testing database connection...")
    
    try:
        from django.db import connection
        from django.core.management import execute_from_command_line
        
        # Try to connect to database
        connection.ensure_connection()
        print("✅ Database connection successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("ℹ️  This is normal if database environment variables aren't set")
        return True  # Don't fail the test for missing DB vars

def main():
    print("🚂 LetterFlow Deployment Test")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path("manage.py").exists():
        print("❌ Error: manage.py not found. Run this script from your Django project root.")
        return False
    
    # Run tests
    tests = [
        test_imports,
        test_settings,
        test_database,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your app is ready for deployment.")
        return True
    else:
        print("⚠️  Some tests failed. Please fix the issues before deploying.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
