from django import forms
from .models import Appointment
from .models import RecurringAppointment

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
