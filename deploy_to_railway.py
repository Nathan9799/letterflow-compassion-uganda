#!/usr/bin/env python3
"""
Deployment helper script for Railway
This script helps you set up your Django app for Railway deployment
"""

import os
import secrets
import string
from pathlib import Path

def generate_secret_key():
    """Generate a secure Django secret key"""
    alphabet = string.ascii_letters + string.digits + string.punctuation
    return ''.join(secrets.choice(alphabet) for _ in range(50))

def main():
    print("🚂 Railway Deployment Helper for LetterFlow")
    print("=" * 50)
    
    # Generate secret key
    secret_key = generate_secret_key()
    print(f"\n🔑 Generated SECRET_KEY:")
    print(f"{secret_key}")
    
    print("\n📋 Next Steps:")
    print("1. Go to Railway dashboard (https://railway.app)")
    print("2. Create a new project")
    print("3. Connect your GitHub repository")
    print("4. Add PostgreSQL database")
    print("5. Set these environment variables:")
    print(f"   - SECRET_KEY: {secret_key}")
    print("   - DJANGO_SETTINGS_MODULE: letterflow.production")
    print("   - RAILWAY_ENVIRONMENT: production")
    
    print("\n⚠️  Important Notes:")
    print("- Keep your SECRET_KEY secure and never commit it to version control")
    print("- Railway will automatically provide database environment variables")
    print("- The first deployment will fail - this is normal")
    print("- After first deployment, run migrations manually")
    
    print("\n📚 For detailed instructions, see: RAILWAY_DEPLOYMENT.md")
    
    # Check if we're in the right directory
    if not Path("manage.py").exists():
        print("\n❌ Error: manage.py not found. Run this script from your Django project root.")
        return
    
    # Check if production settings exist
    if not Path("letterflow/production.py").exists():
        print("\n❌ Error: production.py not found. Make sure you have production settings.")
        return
    
    print("\n✅ Your project is ready for Railway deployment!")
    
    # Create a .gitignore entry reminder
    print("\n📝 Add to .gitignore:")
    print("*.env")
    print(".env")
    print("env.local")
    print("staticfiles/")
    print("media/")

if __name__ == "__main__":
    main()
