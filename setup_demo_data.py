#!/usr/bin/env python
"""
Setup script for LetterFlow demo data.
Run this script to populate the database with sample data for testing.
"""

import os
import sys
import django
from datetime import date, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'letterflow.settings')
django.setup()

from accounts.models import User
from org.models import Cluster, FCP, CollectionCentreUser
from shipping.models import Shipment, ShipmentItem

def create_demo_data():
    """Create demo data for testing"""
    print("Creating demo data for LetterFlow...")
    
    # Create SDSA users
    print("Creating SDSA users...")
    sdsa1 = User.objects.create_user(
        username='sdsa1',
        email='sdsa1@compassion.org',
        password='changeme123',
        first_name='John',
        last_name='Doe',
        role='SDSA',
        must_change_password=True
    )
    
    sdsa2 = User.objects.create_user(
        username='sdsa2',
        email='sdsa2@compassion.org',
        password='changeme123',
        first_name='Jane',
        last_name='Smith',
        role='SDSA',
        must_change_password=True
    )
    
    # Create Clusters
    print("Creating clusters...")
    mbarara_cluster = Cluster.objects.create(
        name='Mbarara Cluster',
        sdsa_owner=sdsa1
    )
    
    kampala_cluster = Cluster.objects.create(
        name='Kampala Cluster',
        sdsa_owner=sdsa2
    )
    
    jinja_cluster = Cluster.objects.create(
        name='Jinja Cluster',
        sdsa_owner=sdsa1
    )
    
    # Create FCPs
    print("Creating FCPs...")
    
    # Mbarara Cluster FCPs
    mbarara_cc = FCP.objects.create(
        code='UG0249',
        name='Mbarara Central Church',
        cluster=mbarara_cluster,
        is_collection_centre=True
    )
    
    FCP.objects.create(
        code='UG0250',
        name='Ruharo Church',
        cluster=mbarara_cluster,
        is_collection_centre=False
    )
    
    FCP.objects.create(
        code='UG0251',
        name='Kashari Church',
        cluster=mbarara_cluster,
        is_collection_centre=False
    )
    
    # Kampala Cluster FCPs
    kampala_cc = FCP.objects.create(
        code='UG0100',
        name='Kampala Central Church',
        cluster=kampala_cluster,
        is_collection_centre=True
    )
    
    FCP.objects.create(
        code='UG0101',
        name='Nakawa Church',
        cluster=kampala_cluster,
        is_collection_centre=False
    )
    
    FCP.objects.create(
        code='UG0102',
        name='Makindye Church',
        cluster=kampala_cluster,
        is_collection_centre=False
    )
    
    # Jinja Cluster FCPs
    jinja_cc = FCP.objects.create(
        code='UG0300',
        name='Jinja Central Church',
        cluster=jinja_cluster,
        is_collection_centre=True
    )
    
    FCP.objects.create(
        code='UG0301',
        name='Njeru Church',
        cluster=jinja_cluster,
        is_collection_centre=False
    )
    
    # Create Collection Centre Users
    print("Creating Collection Centre users...")
    cc1 = User.objects.create_user(
        username='cc_mbarara',
        email='cc.mbarara@compassion.org',
        password='changeme123',
        first_name='Peter',
        last_name='Mukisa',
        role='CC',
        must_change_password=True
    )
    
    cc2 = User.objects.create_user(
        username='cc_kampala',
        email='cc.kampala@compassion.org',
        password='changeme123',
        first_name='Sarah',
        last_name='Nakato',
        role='CC',
        must_change_password=True
    )
    
    cc3 = User.objects.create_user(
        username='cc_jinja',
        email='cc.jinja@compassion.org',
        password='changeme123',
        first_name='David',
        last_name='Ochieng',
        role='CC',
        must_change_password=True
    )
    
    # Link CC users to their FCPs
    CollectionCentreUser.objects.create(user=cc1, fcp=mbarara_cc)
    CollectionCentreUser.objects.create(user=cc2, fcp=kampala_cc)
    CollectionCentreUser.objects.create(user=cc3, fcp=jinja_cc)
    
    # Create sample shipments
    print("Creating sample shipments...")
    
    # Outgoing shipment from Mbarara
    outgoing1 = Shipment.objects.create(
        direction='OUT',
        cluster=mbarara_cluster,
        collection_centre=mbarara_cc,
        estimated_delivery_date=date.today() + timedelta(days=7),
        notes='Monthly letter materials for Mbarara cluster',
        status='CREATED',
        created_by=sdsa1
    )
    
    # Add FCP items to outgoing shipment
    for fcp in mbarara_cluster.fcps.filter(is_collection_centre=False):
        ShipmentItem.objects.create(
            shipment=outgoing1,
            fcp=fcp,
            qty_planned=50
        )
    
    # Return shipment to Mbarara
    return1 = Shipment.objects.create(
        direction='RET',
        cluster=mbarara_cluster,
        collection_centre=mbarara_cc,
        estimated_delivery_date=date.today() + timedelta(days=5),
        notes='Completed letters from Mbarara FCPs',
        status='CREATED',
        created_by=cc1
    )
    
    # Add FCP items to return shipment
    for fcp in mbarara_cluster.fcps.filter(is_collection_centre=False):
        ShipmentItem.objects.create(
            shipment=return1,
            fcp=fcp,
            qty_planned=45
        )
    
    print("\n✅ Demo data created successfully!")
    print("\n📋 Login Credentials:")
    print("=" * 50)
    print("Admin User:")
    print("  Username: admin")
    print("  Password: (as set during superuser creation)")
    print("\nSDSA Users:")
    print("  Username: sdsa1, Password: changeme123")
    print("  Username: sdsa2, Password: changeme123")
    print("\nCollection Centre Users:")
    print("  Username: cc_mbarara, Password: changeme123")
    print("  Username: cc_kampala, Password: changeme123")
    print("  Username: cc_jinja, Password: changeme123")
    print("\n⚠️  IMPORTANT: All users must change their password on first login!")
    print("\n🌐 Access the system at: http://localhost:8000/")
    print("🔧 Admin panel at: http://localhost:8000/admin/")

if __name__ == '__main__':
    try:
        create_demo_data()
    except Exception as e:
        print(f"❌ Error creating demo data: {e}")
        sys.exit(1)
