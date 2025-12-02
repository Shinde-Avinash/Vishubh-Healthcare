"""
Email reminder utilities for appointment notifications
"""
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from datetime import datetime, timedelta
from .models import Appointment


def send_appointment_reminder(appointment):
    """
    Send email reminder for an appointment
    
    Args:
        appointment: Appointment instance
        
    Returns:
        bool: True if reminder sent successfully
    """
    if appointment.reminder_sent:
        return False
    
    # Send reminder to patient
    patient_sent = send_patient_reminder(appointment)
    
    # Send reminder to doctor (if assigned)
    doctor_sent = True
    if appointment.doctor:
        doctor_sent = send_doctor_reminder(appointment)
    
    # Mark reminder as sent if both succeeded
    if patient_sent and doctor_sent:
        appointment.reminder_sent = True
        appointment.save()
        return True
    
    return False


def send_patient_reminder(appointment):
    """Send reminder email to patient"""
    patient = appointment.patient
    subject = f'Appointment Reminder - {appointment.appointment_date}'
    
    message = f"""
Dear {patient.user.get_full_name()},

This is a reminder for your upcoming appointment:

Doctor: Dr. {appointment.doctor.user.get_full_name() if appointment.doctor else 'To be assigned'}
Specialization: {appointment.doctor.specialization if appointment.doctor else 'N/A'}
Date: {appointment.appointment_date.strftime('%B %d, %Y')}
Time: {appointment.appointment_time.strftime('%I:%M %p')}
Status: {appointment.get_status_display()}

Please arrive 10 minutes before your scheduled time.

If you need to reschedule or cancel, please contact us as soon as possible.

Thank you,
Vishubh Healthcare Team
"""
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [patient.user.email],
            fail_silently=False,
        )
        print(f"✓ Reminder sent to patient: {patient.user.email}")
        return True
    except Exception as e:
        print(f"✗ Failed to send reminder to patient: {e}")
        return False


def send_doctor_reminder(appointment):
    """Send reminder email to doctor"""
    doctor = appointment.doctor
    if not doctor:
        return True
    
    subject = f'Appointment Reminder - {appointment.appointment_date}'
    
    message = f"""
Dear Dr. {doctor.user.get_full_name()},

This is a reminder for your upcoming appointment:

Patient: {appointment.patient.user.get_full_name()}
Age: {appointment.patient.age if appointment.patient.age else 'N/A'}
Contact: {appointment.patient.contact}
Date: {appointment.appointment_date.strftime('%B %d, %Y')}
Time: {appointment.appointment_time.strftime('%I:%M %p')}
Symptoms: {appointment.symptoms}

Status: {appointment.get_status_display()}

Please review the patient details before the appointment.

Thank you,
Vishubh Healthcare Team
"""
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [doctor.user.email],
            fail_silently=False,
        )
        print(f"✓ Reminder sent to doctor: {doctor.user.email}")
        return True
    except Exception as e:
        print(f"✗ Failed to send reminder to doctor: {e}")
        return False


def get_appointments_needing_reminders():
    """
    Get appointments that need reminders
    
    Returns:
        QuerySet: Appointments scheduled for tomorrow that haven't received reminders
    """
    tomorrow = datetime.now().date() + timedelta(days=1)
    
    appointments = Appointment.objects.filter(
        appointment_date=tomorrow,
        reminder_sent=False,
        status__in=['pending', 'confirmed']
    ).select_related('patient__user', 'doctor__user')
    
    return appointments


def send_all_reminders():
    """
    Send reminders for all eligible appointments
    
    Returns:
        dict: Statistics about sent reminders
    """
    appointments = get_appointments_needing_reminders()
    
    total = appointments.count()
    sent = 0
    failed = 0
    
    print(f"\n{'='*60}")
    print(f"Sending appointment reminders for {total} appointments...")
    print(f"{'='*60}\n")
    
    for appointment in appointments:
        if send_appointment_reminder(appointment):
            sent += 1
        else:
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Reminder Summary:")
    print(f"  Total: {total}")
    print(f"  Sent: {sent}")
    print(f"  Failed: {failed}")
    print(f"{'='*60}\n")
    
    return {
        'total': total,
        'sent': sent,
        'failed': failed
    }
