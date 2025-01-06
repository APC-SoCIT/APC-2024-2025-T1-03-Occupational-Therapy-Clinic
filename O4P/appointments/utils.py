from .models import Appointment
from datetime import timedelta

def generate_recurring_appointments(recurring_appointment):
    """
    Generate appointments based on the recurrence pattern in RecurringAppointment
    while ensuring no conflicts with existing appointments.
    """
    # Map recurrence patterns to timedelta
    recurrence_map = {
        'daily': timedelta(days=1),
        'weekly': timedelta(weeks=1),
        'bi-weekly': timedelta(weeks=2),
        'monthly': timedelta(weeks=4),  # Approximation for simplicity
    }

    # Get the recurrence interval
    interval = recurrence_map[recurring_appointment.recurrence_pattern]

    # Start creating appointments
    current_date = recurring_appointment.start_date
    appointments = []

    for _ in range(recurring_appointment.number_of_occurrences):
        # Check for conflicts
        conflict = Appointment.objects.filter(
            therapist=recurring_appointment.therapist,
            date=current_date,
            start_time=recurring_appointment.start_time,
        ).exists()

        if conflict:
            raise ValueError(f"Conflict detected: Appointment already exists on {current_date} at {recurring_appointment.start_time}")

        # Add appointment to the list if no conflict
        appointments.append(
            Appointment(
                patient=recurring_appointment.patient,
                therapist=recurring_appointment.therapist,
                date=current_date,
                start_time=recurring_appointment.start_time,
                status='scheduled',
            )
        )
        current_date += interval

    # Bulk create appointments
    Appointment.objects.bulk_create(appointments)
