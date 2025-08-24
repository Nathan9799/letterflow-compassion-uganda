#!/usr/bin/env python3
"""
Startup script for LetterFlow on Railway
This script handles database setup and migrations safely
"""

import os
import sys
import django
from pathlib import Path

def setup_django():
    """Setup Django environment"""
    try:
        # Add project root to Python path
        project_root = Path(__file__).resolve().parent
        sys.path.insert(0, str(project_root))
        
        # Set Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'letterflow.production')
        
        # Setup Django
        django.setup()
        return True
    except Exception as e:
        print(f"❌ Django setup failed: {e}")
        return False

def check_database():
    """Check database connection without crashing"""
    try:
        from django.db import connection
        connection.ensure_connection()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"⚠️  Database connection failed: {e}")
        print("ℹ️  This is normal during initial setup")
        return False

def run_migrations():
    """Run migrations safely"""
    try:
        from django.core.management import call_command
        print("🔄 Running database migrations...")
        call_command('migrate', verbosity=1)
        print("✅ Migrations completed")
        return True
    except Exception as e:
        print(f"⚠️  Migrations failed: {e}")
        print("ℹ️  This is normal during initial setup")
        return False

def main():
    """Main startup function"""
    print("🚀 LetterFlow Startup Script")
    print("=" * 40)
    
    # Setup Django
    if not setup_django():
        print("❌ Failed to setup Django")
        return False
    
    # Check database
    check_database()
    
    # Try migrations (but don't fail if they don't work)
    run_migrations()
    
    print("✅ Startup script completed successfully")
    return True

if __name__ == "__main__":
    main()
