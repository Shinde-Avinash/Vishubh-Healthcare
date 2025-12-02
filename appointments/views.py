from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, FileResponse, JsonResponse
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Appointment, Invoice
from .forms import AppointmentForm, AppointmentUpdateForm
from accounts.models import Doctor, Patient
from .utils import generate_invoice_pdf
from .payment_utils import create_payment_order, verify_payment_signature
from decimal import Decimal
import json


@login_required
def book_appointment(request):
    """Patient appointment booking view"""
    if request.user.role != 'patient':
        messages.error(request, 'Only patients can book appointments.')
        return redirect('home')
    
    try:
        patient = request.user.patient_profile
        if not patient.verified:
            messages.warning(request, 'Your account must be verified by admin before booking appointments.')
            return redirect('patient_dashboard')
    except Patient.DoesNotExist:
        messages.error(request, 'Patient profile not found.')
        return redirect('home')
    
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.patient = patient
            
            # Check for conflicts before saving
            try:
                appointment.save()
                messages.success(request, 'Appointment booked successfully! Please proceed to payment.')
                return redirect('initiate_payment', appointment_id=appointment.id)
            except ValidationError as e:
                messages.error(request, str(e))
                form.add_error(None, e)
    else:
        form = AppointmentForm()
    
    doctors = Doctor.objects.filter(verified=True)
    return render(request, 'patient/book_appointment.html', {'form': form, 'doctors': doctors})


@login_required
def patient_appointments(request):
    """View patient appointments"""
    if request.user.role != 'patient':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    patient = request.user.patient_profile
    appointments = Appointment.objects.filter(patient=patient).order_by('-appointment_date', '-appointment_time')
    
    return render(request, 'patient/appointments.html', {'appointments': appointments})


@login_required
def doctor_appointments(request):
    """View doctor appointments"""
    if request.user.role != 'doctor':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    doctor = request.user.doctor_profile
    appointments = Appointment.objects.filter(doctor=doctor).order_by('-appointment_date', '-appointment_time')
    
    return render(request, 'doctor/appointments.html', {'appointments': appointments})


@login_required
def admin_manage_appointments(request):
    """Admin appointment management view"""
    if request.user.role != 'admin':
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')
    
    appointments = Appointment.objects.all().order_by('-created_at')
    
    # Handle appointment updates
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        action = request.POST.get('action')
        
        appointment = get_object_or_404(Appointment, id=appointment_id)
        
        if action == 'confirm':
            appointment.status = 'confirmed'
            appointment.save()
            messages.success(request, 'Appointment confirmed successfully.')
        
        elif action == 'complete':
            appointment.status = 'completed'
            appointment.save()
            messages.success(request, 'Appointment marked as completed.')
        
        elif action == 'cancel':
            appointment.status = 'cancelled'
            appointment.save()
            messages.success(request, 'Appointment cancelled.')
        
        elif action == 'assign_doctor':
            doctor_id = request.POST.get('doctor_id')
            if doctor_id:
                doctor = get_object_or_404(Doctor, id=doctor_id)
                appointment.doctor = doctor
                appointment.save()
                messages.success(request, f'Doctor {doctor.user.get_full_name()} assigned successfully.')
        
        return redirect('admin_manage_appointments')
    
    doctors = Doctor.objects.filter(verified=True)
    context = {
        'appointments': appointments,
        'doctors': doctors,
    }
    return render(request, 'admin/manage_appointments.html', context)


@login_required
def generate_invoice(request, appointment_id):
    """Generate invoice for an appointment (Admin only)"""
    if request.user.role != 'admin':
        messages.error(request, 'Access denied. Admin only.')
        return redirect('home')
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    if appointment.status != 'confirmed' and appointment.status != 'completed':
        messages.error(request, 'Can only generate invoice for confirmed or completed appointments.')
        return redirect('admin_manage_appointments')
    
    if not appointment.doctor:
        messages.error(request, 'Please assign a doctor before generating invoice.')
        return redirect('admin_manage_appointments')
    
    # Check if invoice already exists
    try:
        invoice = appointment.invoice
        messages.info(request, 'Invoice already exists for this appointment.')
    except Invoice.DoesNotExist:
        # Create new invoice
        amount = request.POST.get('amount', '500')  # Default consultation fee
        invoice = Invoice.objects.create(
            appointment=appointment,
            amount=Decimal(amount)
        )
        
        # Generate PDF
        pdf_content = generate_invoice_pdf(invoice)
        invoice.pdf_file.save(f'invoice_{invoice.id}.pdf', ContentFile(pdf_content))
        invoice.save()
        
        messages.success(request, 'Invoice generated successfully.')
    
    return redirect('admin_manage_appointments')


@login_required
def view_invoice(request, invoice_id):
    """View invoice details"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    # Check permissions
    if request.user.role == 'patient':
        if invoice.appointment.patient.user != request.user:
            messages.error(request, 'Access denied.')
            return redirect('home')
    elif request.user.role == 'doctor':
        if invoice.appointment.doctor.user != request.user:
            messages.error(request, 'Access denied.')
            return redirect('home')
    elif request.user.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    return render(request, 'invoice_detail.html', {'invoice': invoice})


@login_required
def download_invoice(request, invoice_id):
    """Download invoice PDF"""
    invoice = get_object_or_404(Invoice, id=invoice_id)
    
    # Check permissions
    if request.user.role == 'patient':
        if invoice.appointment.patient.user != request.user:
            messages.error(request, 'Access denied.')
            return redirect('home')
    elif request.user.role == 'doctor':
        if invoice.appointment.doctor.user != request.user:
            messages.error(request, 'Access denied.')
            return redirect('home')
    elif request.user.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # If PDF doesn't exist, generate it
    if not invoice.pdf_file:
        pdf_content = generate_invoice_pdf(invoice)
        invoice.pdf_file.save(f'invoice_{invoice.id}.pdf', ContentFile(pdf_content))
        invoice.save()
    
    # Return PDF file
    response = FileResponse(invoice.pdf_file.open('rb'), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.id}.pdf"'
    return response


@login_required
def doctors_list(request):
    """List all verified doctors (for patients)"""
    if request.user.role != 'patient':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    doctors = Doctor.objects.filter(verified=True)
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        doctors = doctors.filter(
            specialization__icontains=search_query
        ) | doctors.filter(
            user__first_name__icontains=search_query
        ) | doctors.filter(
            user__last_name__icontains=search_query
        )
    
    return render(request, 'patient/doctors_list.html', {'doctors': doctors, 'search_query': search_query})


@login_required
def check_availability(request):
    """AJAX endpoint to check doctor availability"""
    if request.method == 'GET':
        doctor_id = request.GET.get('doctor_id')
        date = request.GET.get('date')
        time = request.GET.get('time')
        
        if not all([doctor_id, date, time]):
            return JsonResponse({'available': True})
        
        try:
            doctor = Doctor.objects.get(id=doctor_id)
            conflicting = Appointment.objects.filter(
                doctor=doctor,
                appointment_date=date,
                appointment_time=time,
                status__in=['pending', 'confirmed']
            ).exists()
            
            return JsonResponse({
                'available': not conflicting,
                'message': 'Time slot is available' if not conflicting else 'This time slot is already booked'
            })
        except Doctor.DoesNotExist:
            return JsonResponse({'available': True})
    
    return JsonResponse({'error': 'Invalid request'}, status=400)


@login_required
def doctor_update_status(request, appointment_id):
    """Allow doctors to update appointment status"""
    if request.user.role != 'doctor':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Verify doctor owns this appointment
    if appointment.doctor.user != request.user:
        messages.error(request, 'You can only update your own appointments.')
        return redirect('doctor_appointments')
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        
        if new_status in ['confirmed', 'completed', 'cancelled']:
            appointment.status = new_status
            appointment.save()
            messages.success(request, f'Appointment status updated to {appointment.get_status_display()}.')
        else:
            messages.error(request, 'Invalid status.')
    
    return redirect('doctor_appointments')


@login_required
def initiate_payment(request, appointment_id):
    """Initiate payment for an appointment"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permissions
    if request.user.role == 'patient':
        if appointment.patient.user != request.user:
            messages.error(request, 'Access denied.')
            return redirect('home')
    elif request.user.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    # Check if already paid
    if appointment.payment_status == 'paid':
        messages.info(request, 'This appointment has already been paid for.')
        return redirect('patient_appointments')
    
    # Create payment order
    try:
        from django.conf import settings
        
        # Check if Razorpay is configured
        if not hasattr(settings, 'RAZORPAY_KEY_ID'):
            # Mock payment for development
            appointment.payment_status = 'paid'
            appointment.payment_id = f'MOCK_{appointment.id}_{timezone.now().timestamp()}'
            appointment.save()
            messages.success(request, 'Payment completed successfully (Development Mode)!')
            return redirect('payment_success', appointment_id=appointment.id)
        
        order_result = create_payment_order(appointment)
        
        if order_result['success']:
            context = {
                'appointment': appointment,
                'order_id': order_result['order_id'],
                'amount': order_result['amount'],
                'currency': order_result['currency'],
                'razorpay_key': settings.RAZORPAY_KEY_ID,
            }
            return render(request, 'appointments/payment_page.html', context)
        else:
            messages.error(request, f'Payment initialization failed: {order_result.get("error")}')
            return redirect('patient_appointments')
    except Exception as e:
        messages.error(request, f'Payment error: {str(e)}')
        return redirect('patient_appointments')


@csrf_exempt
@login_required
def payment_callback(request):
    """Handle payment gateway callback"""
    if request.method == 'POST':
        try:
            payment_id = request.POST.get('razorpay_payment_id')
            order_id = request.POST.get('razorpay_order_id')
            signature = request.POST.get('razorpay_signature')
            appointment_id = request.POST.get('appointment_id')
            
            appointment = get_object_or_404(Appointment, id=appointment_id)
            
            # Verify payment signature
            if verify_payment_signature(order_id, payment_id, signature):
                appointment.payment_status = 'paid'
                appointment.payment_id = payment_id
                appointment.save()
                
                return redirect('payment_success', appointment_id=appointment.id)
            else:
                appointment.payment_status = 'failed'
                appointment.save()
                return redirect('payment_failure', appointment_id=appointment.id)
        except Exception as e:
            messages.error(request, f'Payment verification failed: {str(e)}')
            return redirect('patient_appointments')
    
    return redirect('home')


@login_required
def payment_success(request, appointment_id):
    """Payment success page"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permissions
    if request.user.role == 'patient':
        if appointment.patient.user != request.user:
            messages.error(request, 'Access denied.')
            return redirect('home')
    elif request.user.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    return render(request, 'appointments/payment_success.html', {'appointment': appointment})


@login_required
def payment_failure(request, appointment_id):
    """Payment failure page"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    
    # Check permissions
    if request.user.role == 'patient':
        if appointment.patient.user != request.user:
            messages.error(request, 'Access denied.')
            return redirect('home')
    elif request.user.role != 'admin':
        messages.error(request, 'Access denied.')
        return redirect('home')
    
    return render(request, 'appointments/payment_failure.html', {'appointment': appointment})
