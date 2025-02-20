from django.db import models
from django.contrib.auth.models import User
from patients.models import PatientInformation as Patient
from datetime import timedelta, datetime
from accounts.models import TherapistInformation as Therapist
from accounts.models import GuardianInformation as Guardian
from django.core.validators import RegexValidator

class Appointment(models.Model):
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE, related_name="therapist_appointments")
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name="appointments", blank=True, null=True)  #Allow null for non-registered users
    first_name = models.CharField(max_length=50, blank=True, null=True)  #Store first name for non-registered users
    last_name = models.CharField(max_length=50, blank=True, null=True)  #Store last name for non-registered users
    date = models.DateField()
    start_time = models.TimeField()
    status = models.CharField(
        max_length=50,
        choices=[
            ('scheduled', 'Scheduled'),
            ('completed', 'Completed'),
            ('canceled', 'Canceled'),
        ],
        default='scheduled'
    )

    def __str__(self):
        return f"Appointment with {self.therapist.first_name} on {self.date}"

class AppointmentRequest(models.Model):
    # Non-registered user details
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    contact_number = models.CharField(
        max_length=13,  
        validators=[
            RegexValidator(
                regex=r'^(\+63|0)9\d{9}$',  
                message="Phone number must be entered in the format: '+639123456789' or '09123456789'."
            )
        ]
    )

    therapist = models.ForeignKey(
        Therapist,
        on_delete=models.CASCADE,
        related_name="appointment_requests"
    )

    # Requested new appointment details
    requested_date = models.DateField()
    requested_time = models.TimeField()

    # Store the original appointment details before rescheduling
    original_date = models.DateField(blank=True, null=True)
    original_time = models.TimeField(blank=True, null=True)

    notes = models.TextField(blank=True, null=True)

    # Request status
    status = models.CharField(
        max_length=50,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('declined', 'Declined'),
        ],
        default='pending'
    )

    def __str__(self):
        return f"Request from {self.first_name} {self.last_name} with {self.therapist} on {self.requested_date}"


class RecurringAppointment(models.Model):
    patient = models.ForeignKey(
        Patient,
        on_delete=models.CASCADE,
        related_name="recurring_appointments"
    )

    therapist = models.ForeignKey(
        Therapist,  #Use TherapistInformation instead of User
        on_delete=models.CASCADE,
        related_name="therapist_recurring_appointments"
    )

    start_date = models.DateField()
    start_time = models.TimeField()
    recurrence_pattern = models.CharField(
        max_length=50,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('bi-weekly', 'Bi-Weekly'),
            ('monthly', 'Monthly'),
        ],
        default='weekly'
    )
    number_of_occurrences = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.patient} - Recurring {self.recurrence_pattern} with {self.therapist.first_name} {self.therapist.last_name}"