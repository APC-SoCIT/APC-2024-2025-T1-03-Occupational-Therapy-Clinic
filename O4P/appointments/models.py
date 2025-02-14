from django.db import models
from django.contrib.auth.models import User
from patients.models import PatientInformation 
from datetime import timedelta, datetime
from accounts.models import TherapistInformation as Therapist

class Appointment(models.Model):
    guardian = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="appointments",
        blank=True,
        null=True
        )  # Guardians manage appointments
    
    patient = models.ForeignKey(
        PatientInformation, 
        on_delete=models.CASCADE, 
        related_name="appointments",
        blank=True,
        null=True  # ✅ Allow patient to be NULL for non-user requests
        )  # Reference PatientInformation
    
    therapist = models.ForeignKey(
        Therapist, 
        on_delete=models.CASCADE, 
        related_name="therapist_appointments", 
        limit_choices_to={'account_id__groups__name': 'Therapist'}  # ✅ Fixing reference to groups
    )
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
        if self.patient:
            return f"{self.patient} with {self.therapist} on {self.date}"
        return f"Non-User Appointment with {self.therapist} on {self.date}"  # ✅ Handle non-user appointments


class AppointmentRequest(models.Model):
    # Non-registered user details
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)


    therapist = models.ForeignKey(
        Therapist,  # ✅ Use TherapistInformation instead of User
        on_delete=models.CASCADE,
        related_name="appointment_requests"
    )

    # Appointment details
    requested_date = models.DateField()
    requested_time = models.TimeField()
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
        PatientInformation,
        on_delete=models.CASCADE,
        related_name="recurring_appointments"
    )

    therapist = models.ForeignKey(
        Therapist,  # ✅ Use TherapistInformation instead of User
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
