# LetterFlow - Letter Tracking System

A comprehensive Django-based web application designed to streamline the flow of sponsored children's letters within Compassion International Uganda. The system ensures accountability, transparency, and efficiency in monitoring how letters move across different stages of the delivery process.

## 🎯 Project Overview

LetterFlow digitizes the letter tracking workflow between:
- **SDSA (Sponsor Donor Service Associate)** - Based at the National Office
- **Collection Centres** - Designated frontline church partners
- **FCPs (Frontline Church Partners)** - Individual churches under each cluster
- **Clusters** - Groups of FCPs connected through a Collection Centre

## ✨ Key Features

### 🔐 Role-Based Access Control
- **Admin**: Full system management, user creation, and oversight
- **SDSA**: Manage assigned clusters, create outgoing shipments, track returns
- **Collection Centre**: Confirm incoming shipments, create return shipments

### 📦 Shipment Lifecycle Management
- **Outgoing Flow**: SDSA → Collection Centre → FCPs
- **Return Flow**: FCPs → Collection Centre → SDSA
- **Status Tracking**: Created → Received → Distributed/Posted
- **Discrepancy Handling**: Track planned vs. received quantities

### 📊 Comprehensive Reporting
- Monthly statistics by cluster and direction
- Turnaround time metrics
- Performance insights and success rates
- CSV export functionality

### 🎨 Modern UI/UX
- Responsive Bootstrap 5 design
- Compassion International Uganda blue theme
- Intuitive navigation and workflows
- Mobile-friendly interface

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd CTS
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Main app: http://localhost:8000/
   - Admin panel: http://localhost:8000/admin/

## 🏗️ System Setup

### 1. Initial Configuration
After creating your superuser, follow this sequence:

1. **Create SDSA Users**
   - Go to Admin → Users
   - Create users with role "SDSA"
   - Set temporary passwords (users must change on first login)

2. **Create Clusters**
   - Go to Admin → Clusters
   - Create clusters and assign SDSA owners

3. **Create FCPs**
   - Go to Admin → FCPs
   - Create FCPs under each cluster
   - Mark exactly one FCP per cluster as Collection Centre

4. **Create Collection Centre Users**
   - Go to Admin → Collection Centre Users
   - Link CC users to their respective FCPs

### 2. User Onboarding
- Users receive credentials with temporary passwords
- First login requires password change
- Role-based access is automatically enforced

## 📱 Usage Guide

### For SDSA Users
1. **Dashboard**: View managed clusters and pending returns
2. **Create Outgoing**: Select cluster, set ETA, allocate packages per FCP
3. **Track Returns**: Monitor incoming return shipments
4. **Mark Posted**: Finalize processed return shipments

### For Collection Centre Users
1. **Dashboard**: View incoming shipments and recent activity
2. **Confirm Receipt**: Verify received quantities and note discrepancies
3. **Create Returns**: Package and track return shipments
4. **Mark Distributed**: Optional tracking of FCP distribution

### For Administrators
1. **User Management**: Create and manage all user accounts
2. **System Configuration**: Manage clusters, FCPs, and relationships
3. **Reports**: Access comprehensive analytics and export data
4. **System Monitoring**: Track overall system performance

## 🔧 Technical Details

### Architecture
- **Backend**: Django 5.2.5 with custom User model
- **Frontend**: Bootstrap 5 with Django templates
- **Database**: SQLite (development) / PostgreSQL (production)
- **Timezone**: Africa/Kampala

### Key Models
- **User**: Custom user model with roles and password management
- **Cluster**: Organizational unit managed by SDSA
- **FCP**: Frontline Church Partner with collection centre designation
- **Shipment**: Core entity tracking letter flow
- **ShipmentItem**: Per-FCP allocation and receipt tracking

### Security Features
- Role-based access control
- Forced password change on first login
- CSRF protection
- Server-side validation
- Audit trail for all actions

## 📁 Project Structure

```
CTS/
├── letterflow/          # Main Django project
├── accounts/            # Custom user management
├── org/                 # Organization models (Cluster, FCP)
├── shipping/            # Core shipment functionality
├── templates/           # HTML templates
│   ├── base.html       # Base template
│   ├── shipping/       # Shipping templates
│   └── registration/   # Auth templates
├── static/              # Static files (CSS, JS)
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🚨 Important Notes

### Constraints
- Exactly one Collection Centre per cluster
- FCP codes must be unique within a cluster
- Shipments cannot be created for clusters without Collection Centres
- Collection Centre FCPs are excluded from outgoing shipments

### Validation Rules
- At least one FCP must be selected per shipment
- Quantities must be greater than 0
- Duplicate FCPs are not allowed in the same shipment
- Discrepancy notes required when planned ≠ received

## 🔄 Deployment

### Production Considerations
1. **Database**: Use PostgreSQL for production
2. **Static Files**: Configure proper static file serving
3. **Security**: Update SECRET_KEY and disable DEBUG
4. **HTTPS**: Enable SSL/TLS encryption
5. **Backup**: Implement regular database backups

### Environment Variables
```bash
DEBUG=False
SECRET_KEY=your-secure-secret-key
DATABASE_URL=postgresql://user:pass@host:port/db
ALLOWED_HOSTS=yourdomain.com
```

## 🤝 Contributing

1. Follow Django coding standards
2. Test all functionality thoroughly
3. Update documentation for new features
4. Ensure responsive design compatibility

## 📞 Support

For technical support or questions:
- Check the admin documentation
- Review the inline help text throughout the application
- Contact the system administrator

## 📄 License

This project is developed for Compassion International Uganda. All rights reserved.

---

**LetterFlow** - Streamlining letter tracking for sponsored children with love and efficiency. ❤️
