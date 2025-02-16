from django import forms
from .models import Appointment
from .models import RecurringAppointment
from .models import AppointmentRequest
from therapists.models import AvailableSlot
from accounts.models import TherapistInformation as Therapist
from patients.models import PatientInformation as Patient
from django.contrib.auth.models import User
from datetime import datetime

class AppointmentForm(forms.ModelForm):
    therapist = forms.ModelChoiceField(queryset=Therapist.objects.only("id", "first_name", "last_name"), required=True)
    patient = forms.ModelChoiceField(queryset=Patient.objects.values("id", "first_name", "last_name"), required=False)

    class Meta:
        model = Appointment
        fields = ['therapist', 'patient', 'date', 'start_time', 'status']

    def __init__(self, *args, **kwargs):
        super(AppointmentForm, self).__init__(*args, **kwargs)

        # ✅ Ensure therapists are correctly referenced
        self.fields['therapist'].queryset = Therapist.objects.all()
        
        # ✅ Ensure patients are correctly referenced
        self.fields['patient'].queryset = Patient.objects.all()

class RecurringAppointmentForm(forms.ModelForm):
    class Meta:
        model = RecurringAppointment
        fields = ['patient', 'therapist', 'start_date', 'start_time', 'recurrence_pattern', 'number_of_occurrences']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
        }

class AppointmentRequestForm(forms.ModelForm):
    therapist = forms.ModelChoiceField(
        queryset=Therapist.objects.only("id", "first_name", "last_name"),
        required=True,
        label="Select Therapist"
    )
    requested_time = forms.ChoiceField(choices=[], required=True)

    class Meta:
        model = AppointmentRequest
        fields = ['first_name', 'last_name', 'therapist', 'requested_date', 'requested_time', 'contact_number', 'notes']
        widgets = {
            'requested_date': forms.DateInput(attrs={'type': 'date'}),
            'requested_time': forms.Select(),
            'contact_number': forms.TextInput(attrs={'placeholder': 'Enter contact number'}),
        }

    def __init__(self, *args, **kwargs):
        super(AppointmentRequestForm, self).__init__(*args, **kwargs)

        if 'therapist' in self.data and 'requested_date' in self.data:
            try:
                therapist_id = int(self.data.get('therapist'))
                requested_date = self.data.get('requested_date')

                # ✅ Convert requested_date into the weekday name
                day_name = datetime.strptime(requested_date, "%Y-%m-%d").strftime("%A").lower()

                # ✅ Fetch available slots for the selected therapist on that day
                therapist_slots = AvailableSlot.objects.filter(therapist_id=therapist_id, day=day_name)

                # ✅ Debugging: Print available slots
                available_choices = [(slot.start_time.strftime('%H:%M'), slot.start_time.strftime('%H:%M')) for slot in therapist_slots]
                print(f"Available slots for therapist {therapist_id} on {day_name}:", available_choices)

                # ✅ Set valid requested_time choices
                self.fields['requested_time'].choices = available_choices

            except (ValueError, TypeError) as e:
                print(f"Error processing available slots: {e}")  # Debugging log
                pass  # Ignore invalid input