from django import forms
from .models import Appointment
from .models import RecurringAppointment

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'therapist', 'date', 'start_time', 'status']

class RecurringAppointmentForm(forms.ModelForm):
    class Meta:
        model = RecurringAppointment
        fields = ['patient', 'therapist', 'start_date', 'start_time', 'recurrence_pattern', 'number_of_occurrences']
