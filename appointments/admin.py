from django.contrib import admin
from .models import Appointment, Invoice


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """Appointment admin"""
    list_display = ('patient', 'doctor', 'appointment_date', 'appointment_time', 'status', 'created_at')
    list_filter = ('status', 'appointment_date', 'created_at')
    search_fields = ('patient__user__username', 'doctor__user__username', 'symptoms')
    actions = ['confirm_appointments', 'complete_appointments']
    
    def confirm_appointments(self, request, queryset):
        queryset.update(status='confirmed')
    confirm_appointments.short_description = "Confirm selected appointments"
    
    def complete_appointments(self, request, queryset):
        queryset.update(status='completed')
    complete_appointments.short_description = "Mark selected appointments as completed"


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    """Invoice admin"""
    list_display = ('id', 'appointment', 'amount', 'generated_date')
    list_filter = ('generated_date',)
    search_fields = ('appointment__patient__user__username',)
