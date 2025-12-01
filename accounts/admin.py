from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Doctor, Patient


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin"""
    list_display = ('username', 'email', 'first_name', 'last_name', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Role Information', {'fields': ('role',)}),
    )


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    """Doctor admin"""
    list_display = ('user', 'specialization', 'contact', 'experience_years', 'verified', 'created_at')
    list_filter = ('verified', 'specialization', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'specialization')
    actions = ['verify_doctors']
    
    def verify_doctors(self, request, queryset):
        queryset.update(verified=True)
    verify_doctors.short_description = "Verify selected doctors"


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    """Patient admin"""
    list_display = ('user', 'contact', 'age', 'blood_group', 'verified', 'created_at')
    list_filter = ('verified', 'blood_group', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'contact')
    actions = ['verify_patients']
    
    def verify_patients(self, request, queryset):
        queryset.update(verified=True)
    verify_patients.short_description = "Verify selected patients"
