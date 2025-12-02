from django.db import models
from django.core.exceptions import ValidationError
from accounts.models import User, Doctor, Patient
from datetime import datetime, timedelta


class Appointment(models.Model):
    """Appointment model for managing doctor-patient appointments"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Payment Pending'),
        ('paid', 'Paid'),
        ('failed', 'Payment Failed'),
        ('refunded', 'Refunded'),
    )
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments')
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    symptoms = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    
    # Payment fields
    payment_status = models.CharField(max_length=15, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2, default=500.00)
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    
    # Reminder tracking
    reminder_sent = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        doctor_name = f"Dr. {self.doctor.user.get_full_name()}" if self.doctor else "Unassigned"
        return f"{self.patient.user.get_full_name()} - {doctor_name} on {self.appointment_date}"
    
    def clean(self):
        """Validate appointment to prevent conflicts"""
        if self.doctor and self.appointment_date and self.appointment_time:
            # Check for conflicting appointments
            conflicting = Appointment.objects.filter(
                doctor=self.doctor,
                appointment_date=self.appointment_date,
                appointment_time=self.appointment_time,
                status__in=['pending', 'confirmed']
            ).exclude(pk=self.pk)
            
            if conflicting.exists():
                raise ValidationError(
                    f'This time slot is already booked. Dr. {self.doctor.user.get_full_name()} '
                    f'has another appointment at {self.appointment_time} on {self.appointment_date}.'
                )
    
    def save(self, *args, **kwargs):
        """Override save to run validation"""
        self.clean()
        super().save(*args, **kwargs)
    
    def is_upcoming(self):
        """Check if appointment is upcoming (within next 24 hours)"""
        appointment_datetime = datetime.combine(self.appointment_date, self.appointment_time)
        now = datetime.now()
        time_until = appointment_datetime - now
        return timedelta(hours=0) < time_until <= timedelta(hours=24)
    
    class Meta:
        ordering = ['-appointment_date', '-appointment_time']
        # Prevent double booking at database level
        constraints = [
            models.UniqueConstraint(
                fields=['doctor', 'appointment_date', 'appointment_time'],
                condition=models.Q(status__in=['pending', 'confirmed']),
                name='unique_doctor_appointment_slot'
            )
        ]


class Invoice(models.Model):
    """Invoice model for appointment billing"""
    PAYMENT_STATUS_CHOICES = (
        ('pending', 'Payment Pending'),
        ('paid', 'Paid'),
        ('failed', 'Payment Failed'),
        ('refunded', 'Refunded'),
    )
    
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='invoice')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    generated_date = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='invoices/', blank=True, null=True)
    
    # Payment tracking
    payment_status = models.CharField(max_length=15, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_id = models.CharField(max_length=100, blank=True, null=True)
    payment_date = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"Invoice #{self.id} - {self.appointment.patient.user.get_full_name()} - ₹{self.amount}"
    
    class Meta:
        ordering = ['-generated_date']
