# Vishubh Doctors Appointment Booking System

A comprehensive Django-based healthcare appointment management platform with role-based access for Admins, Doctors, and Patients.

## Features

### For Patients
- Register and create profile
- Browse verified doctors by specialization
- Book appointments with preferred doctors
- Track appointment status (Pending/Confirmed/Completed)
- Download digital invoices

### For Doctors
- Register with specialization and credentials
- View assigned appointments
- Access patient details and symptoms
- Manage profile information

### For Admins
- Verify doctor and patient accounts
- Manage all users (view, verify, delete)
- Approve/reject appointment requests
- Assign doctors to patients
- Generate and manage invoices
- View comprehensive dashboard statistics

## Technology Stack

- **Backend**: Django 4.2.7 (Python)
- **Database**: SQLite (default)
- **Frontend**: HTML5, CSS3, JavaScript
- **PDF Generation**: ReportLab
- **Image Processing**: Pillow

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Clone or Download the Project
```bash
cd "c:\Users\om\Desktop\TEMP_FILES\2-Avinash\Python\Projects\Vishubh Doctors Appointment Booking System"
```

### Step 2: Create Virtual Environment (Already created)
```bash
python -m venv venv
```

### Step 3: Activate Virtual Environment
**Windows:**
```bash
.\venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### Step 4: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 5: Run Migrations (Already completed)
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 6: Create Admin Superuser
```bash
python manage.py createsuperuser
```
Follow the prompts to create an admin account with username, email, and password.

### Step 7: Run Development Server
```bash
python manage.py runserver
```

The application will be available at: **http://127.0.0.1:8000/**

## Usage Guide

### Initial Setup

1. **Create Admin Account**
   - Run `python manage.py createsuperuser`
   - Access Django admin at http://127.0.0.1:8000/admin/
   - Login with superuser credentials

2. **Register Users**
   - Visit http://127.0.0.1:8000/
   - Click "Register as Doctor" or "Register as Patient"
   - Fill in the registration form
   - Wait for admin verification

3. **Admin Verification**
   - Login as admin
   - Go to "Manage Users"
   - Verify pending doctor and patient accounts

### Patient Workflow

1. **Register** → Fill patient registration form
2. **Wait for Verification** → Admin verifies account
3. **Browse Doctors** → View available doctors and specializations
4. **Book Appointment** → Select doctor, date, time, and describe symptoms
5. **Track Status** → Check appointment status in dashboard
6. **Download Invoice** → Once confirmed, download PDF invoice

### Doctor Workflow

1. **Register** → Fill doctor registration form with specialization
2. **Wait for Verification** → Admin verifies credentials
3. **View Appointments** → See assigned appointments
4. **Check Patient Details** → View patient information and symptoms
5. **Update Profile** → Manage professional information

### Admin Workflow

1. **Login** → Use superuser credentials
2. **Verify Users** → Approve doctor and patient registrations
3. **Manage Appointments** → View all appointments
4. **Assign Doctors** → Assign doctors to patient appointments
5. **Confirm Appointments** → Approve pending appointments
6. **Generate Invoices** → Create PDF invoices for confirmed appointments

## Project Structure

```
Vishubh Doctors Appointment Booking System/
├── accounts/                  # User authentication & management
│   ├── models.py             # User, Doctor, Patient models
│   ├── views.py              # Authentication & profile views
│   ├── forms.py              # Registration & profile forms
│   └── admin.py              # Admin configuration
├── appointments/              # Appointment management
│   ├── models.py             # Appointment, Invoice models
│   ├── views.py              # Booking & management views
│   ├── forms.py              # Appointment forms
│   ├── utils.py              # PDF generation utilities
│   └── admin.py              # Admin configuration
├── templates/                 # HTML templates
│   ├── base.html             # Base template
│   ├── home.html             # Landing page
│   ├── accounts/             # Auth templates
│   ├── admin/                # Admin templates
│   ├── doctor/               # Doctor templates
│   └── patient/              # Patient templates
├── static/                    # Static files
│   ├── css/style.css         # Stylesheet
│   └── js/main.js            # JavaScript
├── media/                     # User uploads
│   └── invoices/             # Generated PDFs
├── vishubh_project/          # Project settings
│   ├── settings.py           # Configuration
│   └── urls.py               # URL routing
├── manage.py                 # Django management
├── requirements.txt          # Dependencies
└── db.sqlite3               # Database
```

## Default Credentials

After creating a superuser, you can:
- **Admin**: Use your superuser credentials
- **Doctor/Patient**: Register through the website

## Features Implemented

✅ User authentication with role-based access (Admin/Doctor/Patient)  
✅ Doctor and patient profile management  
✅ Appointment booking system  
✅ Admin approval workflow  
✅ Doctor assignment to appointments  
✅ PDF invoice generation and download  
✅ Responsive design for mobile and desktop  
✅ Search functionality for doctors  
✅ Dashboard statistics for all user roles  
✅ Status tracking (Pending/Confirmed/Completed/Cancelled)  

## Security Features

- Password hashing using Django's built-in authentication
- CSRF protection on all forms
- Role-based access control
- Input validation and sanitization
- Secure file upload handling

## Troubleshooting

### Port Already in Use
```bash
python manage.py runserver 8080
```

### Database Issues
```bash
python manage.py migrate --run-syncdb
```

### Static Files Not Loading
```bash
python manage.py collectstatic
```

## Future Enhancements

- Email/SMS notifications for appointments
- Online payment integration
- Doctor availability calendar
- Video consultation feature
- Patient medical history
- Multi-language support
- Advanced search filters

## Support

For issues or questions:
- Check the documentation
- Review error logs in the console
- Ensure all dependencies are installed
- Verify database migrations are complete

## License

This project is created for educational purposes as part of the Vishubh AI / Healthcare Web Solution.

## Version

**Version 1.0** - Initial Release

---

**Developed with Django 4.2.7 | Python 3.x | SQLite**
