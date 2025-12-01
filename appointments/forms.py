from django import forms
from .models import Appointment
from accounts.models import Doctor
import datetime


class AppointmentForm(forms.ModelForm):
    """Appointment booking form"""
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.filter(verified=True),
        required=False,
        empty_label="Select a doctor (optional)"
    )
    appointment_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'min': datetime.date.today().isoformat()}),
        help_text="Select appointment date"
    )
    appointment_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'}),
        help_text="Select appointment time"
    )
    
    class Meta:
        model = Appointment
        fields = ('doctor', 'appointment_date', 'appointment_time', 'symptoms')
        widgets = {
            'doctor': forms.Select(attrs={'class': 'form-control'}),
            'symptoms': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Describe your symptoms...'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['doctor'].widget.attrs.update({'class': 'form-control'})
        self.fields['appointment_date'].widget.attrs.update({'class': 'form-control'})
        self.fields['appointment_time'].widget.attrs.update({'class': 'form-control'})

    def clean_appointment_date(self):
        date = self.cleaned_data.get('appointment_date')
        if date and date < datetime.date.today():
            raise forms.ValidationError("Appointment date cannot be in the past.")
        return date


class AppointmentUpdateForm(forms.ModelForm):
    """Form for admin to update appointment"""
    doctor = forms.ModelChoiceField(
        queryset=Doctor.objects.filter(verified=True),
        required=True
    )
    
    class Meta:
        model = Appointment
        fields = ('doctor', 'status', 'appointment_date', 'appointment_time')
        widgets = {
            'appointment_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'appointment_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'doctor': forms.Select(attrs={'class': 'form-control'}),
        }
