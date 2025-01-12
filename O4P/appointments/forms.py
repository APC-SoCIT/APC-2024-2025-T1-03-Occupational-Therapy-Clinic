from django import forms
from .models import Appointment
from .models import RecurringAppointment
from .models import AppointmentRequest

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'therapist', 'date', 'start_time', 'status']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

class RecurringAppointmentForm(forms.ModelForm):
    class Meta:
        model = RecurringAppointment
        fields = ['patient', 'therapist', 'start_date', 'start_time', 'recurrence_pattern', 'number_of_occurrences']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

class AppointmentRequestForm(forms.ModelForm):
    class Meta:
        model = AppointmentRequest
        fields = ['first_name', 'last_name', 'therapist', 'requested_date', 'requested_time', 'contact_number', 'notes']
        widgets = {
            'requested_date': forms.DateInput(attrs={'type': 'date'}),
            'requested_time': forms.TimeInput(attrs={'type': 'time'}),
            'contact_number': forms.TextInput(attrs={'placeholder': 'Enter additional contact info'}),
        }
