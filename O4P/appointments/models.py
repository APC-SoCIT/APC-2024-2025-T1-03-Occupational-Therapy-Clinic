from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta, datetime

class Appointment(models.Model):
    patient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="appointments",
        limit_choices_to={'groups__name': 'Patient'},
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
    # For non-account patients
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    contact_number = models.CharField(max_length=15, blank=True, null=True)

    # Optional reference to a user account
    patient = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='appointment_requests',
        limit_choices_to={'groups__name': 'Patient'},
        blank=True,
        null=True,
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

class NonWorkingDay(models.Model):
    therapist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='non_working_days')
    date = models.DateField()

    def __str__(self):
        return f"{self.therapist.username} - {self.date}"
    
class AppointmentSlot(models.Model):
    therapist = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appointment_slots')
    date = models.DateField()
    start_time = models.TimeField()
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.date} - {self.start_time} ({'Booked' if self.is_booked else 'Available'})"