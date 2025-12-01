from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .forms import DoctorSignUpForm, PatientSignUpForm, DoctorProfileForm, PatientProfileForm
from .models import User, Doctor, Patient
from appointments.models import Appointment


def home(request):
    """Home page view"""
    if request.user.is_authenticated:
        if request.user.role == 'admin':
            return redirect('admin_dashboard')
        elif request.user.role == 'doctor':
            return redirect('doctor_dashboard')
        elif request.user.role == 'patient':
            return redirect('patient_dashboard')
    return render(request, 'home.html')


def user_login(request):
    """Login view for all users"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.get_full_name()}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'accounts/login.html')


@login_required
def user_logout(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')


def doctor_signup(request):
    """Doctor registration view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = DoctorSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Please wait for admin verification.')
            return redirect('login')
    else:
        form = DoctorSignUpForm()
    
    return render(request, 'accounts/signup.html', {'form': form, 'user_type': 'Doctor'})


def patient_signup(request):
    """Patient registration view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = PatientSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Please wait for admin verification.')
            return redirect('login')
    else:
        form = PatientSignUpForm()
    
    return render(request, 'accounts/signup.html', {'form': form, 'user_type': 'Patient'})


# Admin Views
@login_required
def admin_dashboard(request):
    """Admin dashboard view"""
    if request.user.role != 'admin':
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')
    
    context = {
        'total_patients': Patient.objects.count(),
        'total_doctors': Doctor.objects.count(),
        'total_appointments': Appointment.objects.count(),
        'pending_appointments': Appointment.objects.filter(status='pending').count(),
        'confirmed_appointments': Appointment.objects.filter(status='confirmed').count(),
        'pending_doctors': Doctor.objects.filter(verified=False).count(),
        'pending_patients': Patient.objects.filter(verified=False).count(),
    }
    return render(request, 'admin/dashboard.html', context)


@login_required
def admin_manage_users(request):
    """Admin user management view"""
    if request.user.role != 'admin':
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')
    
    doctors = Doctor.objects.all()
    patients = Patient.objects.all()
    
    # Handle verification
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        user_id = request.POST.get('user_id')
        action = request.POST.get('action')
        
        if user_type == 'doctor':
            doctor = get_object_or_404(Doctor, id=user_id)
            if action == 'verify':
                doctor.verified = True
                doctor.save()
                messages.success(request, f'Dr. {doctor.user.get_full_name()} verified successfully.')
            elif action == 'delete':
                doctor.user.delete()
                messages.success(request, 'Doctor account deleted.')
        
        elif user_type == 'patient':
            patient = get_object_or_404(Patient, id=user_id)
            if action == 'verify':
                patient.verified = True
                patient.save()
                messages.success(request, f'{patient.user.get_full_name()} verified successfully.')
            elif action == 'delete':
                patient.user.delete()
                messages.success(request, 'Patient account deleted.')
        
        return redirect('admin_manage_users')
    
    context = {
        'doctors': doctors,
        'patients': patients,
    }
    return render(request, 'admin/manage_users.html', context)


# Doctor Views
@login_required
def doctor_dashboard(request):
    """Doctor dashboard view"""
    if request.user.role != 'doctor':
        messages.error(request, 'Access denied. Doctors only.')
        return redirect('home')
    
    try:
        doctor = request.user.doctor_profile
        if not doctor.verified:
            messages.warning(request, 'Your account is pending verification by admin.')
    except Doctor.DoesNotExist:
        messages.error(request, 'Doctor profile not found.')
        return redirect('home')
    
    appointments = Appointment.objects.filter(doctor=doctor).order_by('-appointment_date', '-appointment_time')
    
    context = {
        'doctor': doctor,
        'appointments': appointments,
        'total_appointments': appointments.count(),
        'pending_appointments': appointments.filter(status='pending').count(),
        'confirmed_appointments': appointments.filter(status='confirmed').count(),
    }
    return render(request, 'doctor/dashboard.html', context)


@login_required
def doctor_profile(request):
    """Doctor profile view"""
    if request.user.role != 'doctor':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    doctor = request.user.doctor_profile
    
    if request.method == 'POST':
        form = DoctorProfileForm(request.POST, instance=doctor)
        if form.is_valid():
            form.save()
            # Update user info
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('doctor_profile')
    else:
        form = DoctorProfileForm(instance=doctor)
    
    return render(request, 'doctor/profile.html', {'form': form, 'doctor': doctor})


# Patient Views
@login_required
def patient_dashboard(request):
    """Patient dashboard view"""
    if request.user.role != 'patient':
        messages.error(request, 'Access denied. Patients only.')
        return redirect('home')
    
    try:
        patient = request.user.patient_profile
        if not patient.verified:
            messages.warning(request, 'Your account is pending verification by admin.')
    except Patient.DoesNotExist:
        messages.error(request, 'Patient profile not found.')
        return redirect('home')
    
    appointments = Appointment.objects.filter(patient=patient).order_by('-appointment_date', '-appointment_time')
    
    context = {
        'patient': patient,
        'appointments': appointments,
        'total_appointments': appointments.count(),
        'pending_appointments': appointments.filter(status='pending').count(),
        'confirmed_appointments': appointments.filter(status='confirmed').count(),
    }
    return render(request, 'patient/dashboard.html', context)


@login_required
def patient_profile(request):
    """Patient profile view"""
    if request.user.role != 'patient':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    patient = request.user.patient_profile
    
    if request.method == 'POST':
        form = PatientProfileForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            # Update user info
            request.user.first_name = form.cleaned_data['first_name']
            request.user.last_name = form.cleaned_data['last_name']
            request.user.email = form.cleaned_data['email']
            request.user.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('patient_profile')
    else:
        form = PatientProfileForm(instance=patient)
    
    return render(request, 'patient/profile.html', {'form': form, 'patient': patient})
