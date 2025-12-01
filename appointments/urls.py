from django.urls import path
from . import views

urlpatterns = [
    # Patient appointment URLs
    path('book/', views.book_appointment, name='book_appointment'),
    path('patient/appointments/', views.patient_appointments, name='patient_appointments'),
    path('doctors/', views.doctors_list, name='doctors_list'),
    
    # Doctor appointment URLs
    path('doctor/appointments/', views.doctor_appointments, name='doctor_appointments'),
    
    # Admin appointment URLs
    path('admin/appointments/', views.admin_manage_appointments, name='admin_manage_appointments'),
    path('admin/generate-invoice/<int:appointment_id>/', views.generate_invoice, name='generate_invoice'),
    
    # Invoice URLs
    path('invoice/<int:invoice_id>/', views.view_invoice, name='view_invoice'),
    path('invoice/<int:invoice_id>/download/', views.download_invoice, name='download_invoice'),
]
