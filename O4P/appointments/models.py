from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, datetime

class Appointment(models.Model):
    patient = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="patient_appointments",
        limit_choices_to={'groups__name': 'Patient'}
    )
    therapist = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="therapist_appointments",
        limit_choices_to={'groups__name': 'Therapist'}
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
        return f"{self.patient.username} with {self.therapist.username} on {self.date}"

    @property
    def end_time(self):
        """Calculate end time dynamically (1 hour after start_time)."""
        return (datetime.combine(self.date, self.start_time) + timedelta(hours=1)).time()


class AppointmentRequest(models.Model):
    patient = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="appointment_requests",
        limit_choices_to={'groups__name': 'Patient'}
    )
    therapist = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name="therapist_requests",
        limit_choices_to={'groups__name': 'Therapist'}
    )
    requested_date = models.DateField()
    requested_time = models.TimeField()
    notes = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=50,
        choices=[
            ('pending', 'Pending'),
            ('approved', 'Approved'),
            ('declined', 'Declined'),
        ],
        default='pending'
    )

    class Meta:
        verbose_name = "Appointment Request"
        verbose_name_plural = "Appointment Requests"

        indexes = [
            models.Index(fields=['patient']),
            models.Index(fields=['therapist']),
        ]

    def __str__(self):
        return f"Request by {self.patient.username} for {self.therapist.username} on {self.requested_date}"


class RecurringAppointment(models.Model):
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recurring_appointments",
        limit_choices_to={'groups__name': 'Patient'}
    )
    therapist = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="therapist_recurring_appointments",
        limit_choices_to={'groups__name': 'Therapist'}
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
        return f"{self.patient.username} - Recurring {self.recurrence_pattern} with {self.therapist.username}"
