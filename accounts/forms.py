from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Doctor, Patient


class DoctorSignUpForm(UserCreationForm):
    """Doctor registration form"""
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    specialization = forms.CharField(max_length=100, required=True)
    contact = forms.CharField(max_length=15, required=True)
    qualification = forms.CharField(max_length=200, required=False)
    experience_years = forms.IntegerField(min_value=0, initial=0)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'doctor'
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Doctor.objects.create(
                user=user,
                specialization=self.cleaned_data['specialization'],
                contact=self.cleaned_data['contact'],
                qualification=self.cleaned_data.get('qualification', ''),
                experience_years=self.cleaned_data['experience_years']
            )
        return user


class PatientSignUpForm(UserCreationForm):
    """Patient registration form"""
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    age = forms.IntegerField(min_value=0, required=False)
    contact = forms.CharField(max_length=15, required=True)
    address = forms.CharField(widget=forms.Textarea, required=False)
    blood_group = forms.CharField(max_length=5, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'patient'
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            Patient.objects.create(
                user=user,
                age=self.cleaned_data.get('age'),
                contact=self.cleaned_data['contact'],
                address=self.cleaned_data.get('address', ''),
                blood_group=self.cleaned_data.get('blood_group', '')
            )
        return user


class DoctorProfileForm(forms.ModelForm):
    """Doctor profile update form"""
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = Doctor
        fields = ('specialization', 'contact', 'qualification', 'experience_years')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email


class PatientProfileForm(forms.ModelForm):
    """Patient profile update form"""
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = Patient
        fields = ('age', 'contact', 'address', 'blood_group')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
