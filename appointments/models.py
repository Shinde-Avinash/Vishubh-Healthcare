from django.db import models
from accounts.models import User, Doctor, Patient


class Appointment(models.Model):
    """Appointment model for managing doctor-patient appointments"""
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, blank=True, related_name='appointments')
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    symptoms = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        doctor_name = f"Dr. {self.doctor.user.get_full_name()}" if self.doctor else "Unassigned"
        return f"{self.patient.user.get_full_name()} - {doctor_name} on {self.appointment_date}"
    
    class Meta:
        ordering = ['-appointment_date', '-appointment_time']


class Invoice(models.Model):
    """Invoice model for appointment billing"""
    appointment = models.OneToOneField(Appointment, on_delete=models.CASCADE, related_name='invoice')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    generated_date = models.DateTimeField(auto_now_add=True)
    pdf_file = models.FileField(upload_to='invoices/', blank=True, null=True)
    
    def __str__(self):
        return f"Invoice #{self.id} - {self.appointment.patient.user.get_full_name()} - ₹{self.amount}"
    
    class Meta:
        ordering = ['-generated_date']
