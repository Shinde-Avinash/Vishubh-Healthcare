# Vishubh Doctors Appointment Booking System - Setup Guide

## Quick Start Guide

### 1. System Requirements
- Python 3.8 or higher
- pip (Python package installer)
- 100MB free disk space
- Modern web browser (Chrome, Firefox, Edge, Safari)

### 2. Installation Steps

#### Step 1: Navigate to Project Directory
```bash
cd "c:\Users\om\Desktop\TEMP_FILES\2-Avinash\Python\Projects\Vishubh Doctors Appointment Booking System"
```

#### Step 2: Activate Virtual Environment
**Windows:**
```bash
.\venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

#### Step 3: Verify Installation
```bash
pip list
```
You should see Django, Pillow, and reportlab installed.

#### Step 4: Create Admin Account
```bash
python manage.py createsuperuser
```

**Example:**
- Username: admin
- Email: admin@vishubh.com
- Password: (enter a secure password)
- Password (again): (confirm password)

#### Step 5: Start the Server
```bash
python manage.py runserver
```

#### Step 6: Access the Application
Open your browser and go to: **http://127.0.0.1:8000/**

### 3. Initial Configuration

#### Create Test Accounts

**Option 1: Through Web Interface**
1. Go to http://127.0.0.1:8000/
2. Click "Register as Doctor" or "Register as Patient"
3. Fill in the form and submit
4. Login as admin to verify accounts

**Option 2: Through Django Admin**
1. Go to http://127.0.0.1:8000/admin/
2. Login with superuser credentials
3. Create users manually

### 4. Testing the System

#### Test as Admin
1. Login at http://127.0.0.1:8000/accounts/login/
2. Go to "Manage Users" to verify pending accounts
3. Go to "Manage Appointments" to handle bookings
4. Generate invoices for confirmed appointments

#### Test as Doctor
1. Register as doctor with specialization
2. Wait for admin verification (or verify yourself as admin)
3. Login and view dashboard
4. Check assigned appointments

#### Test as Patient
1. Register as patient
2. Wait for admin verification (or verify yourself as admin)
3. Login and browse doctors
4. Book an appointment
5. Track appointment status
6. Download invoice once generated

### 5. Common Commands

#### Start Server
```bash
python manage.py runserver
```

#### Create Superuser
```bash
python manage.py createsuperuser
```

#### Make Migrations (after model changes)
```bash
python manage.py makemigrations
python manage.py migrate
```

#### Collect Static Files (for production)
```bash
python manage.py collectstatic
```

#### Run on Different Port
```bash
python manage.py runserver 8080
```

### 6. Database Management

#### Reset Database (if needed)
```bash
# Delete db.sqlite3 file
# Then run:
python manage.py migrate
python manage.py createsuperuser
```

#### View Database
You can use SQLite browser tools or Django admin interface.

### 7. File Locations

- **Database**: `db.sqlite3` (in project root)
- **Uploaded Invoices**: `media/invoices/`
- **Static Files**: `static/` and `staticfiles/`
- **Templates**: `templates/`

### 8. Troubleshooting

#### Problem: Port 8000 already in use
**Solution:**
```bash
python manage.py runserver 8080
```

#### Problem: Static files not loading
**Solution:**
```bash
python manage.py collectstatic --noinput
```

#### Problem: Database errors
**Solution:**
```bash
python manage.py migrate --run-syncdb
```

#### Problem: Module not found
**Solution:**
```bash
pip install -r requirements.txt
```

### 9. Production Deployment (Optional)

For production deployment:
1. Set `DEBUG = False` in settings.py
2. Configure `ALLOWED_HOSTS`
3. Use a production database (PostgreSQL/MySQL)
4. Set up a web server (Nginx/Apache)
5. Use WSGI server (Gunicorn/uWSGI)
6. Configure HTTPS/SSL
7. Set up environment variables for secrets

### 10. Backup and Maintenance

#### Backup Database
```bash
# Simply copy db.sqlite3 to a safe location
copy db.sqlite3 backup_db.sqlite3
```

#### Backup Media Files
```bash
# Copy the entire media folder
xcopy media backup_media /E /I
```

### 11. Development Tips

- Always activate virtual environment before running commands
- Keep requirements.txt updated
- Make migrations after model changes
- Test on different browsers
- Check console for errors
- Use Django debug toolbar for development

### 12. Support Resources

- Django Documentation: https://docs.djangoproject.com/
- Python Documentation: https://docs.python.org/
- ReportLab Documentation: https://www.reportlab.com/docs/

---

## Quick Reference

### URLs
- Home: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/
- Login: http://127.0.0.1:8000/accounts/login/
- Doctor Signup: http://127.0.0.1:8000/accounts/signup/doctor/
- Patient Signup: http://127.0.0.1:8000/accounts/signup/patient/

### Default Ports
- Development Server: 8000
- Alternative: 8080, 8888

### Important Files
- Settings: `vishubh_project/settings.py`
- URLs: `vishubh_project/urls.py`
- Database: `db.sqlite3`

---

**For any issues, check the main README.md file or review the error messages in the console.**
