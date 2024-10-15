from django import forms
from django.core.exceptions import ValidationError

from .models import PatientInformation

class PatientInformationForm(forms.ModelForm):
    class Meta:
        model = PatientInformation
        fields = [
            'first_name', 'last_name', 'date_of_birth', 
            'contact_number', 'city', 'province', 'condition'
        ]
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'date_of_birth': 'Date of Birth',
            'contact_number': 'Contact Number',
            'city': 'City',
            'province': 'Province',
            'condition': 'Medical Condition'
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'province': forms.TextInput(attrs={'class': 'form-control'}),
            'condition': forms.TextInput(attrs={'class': 'form-control'}),
        }