from datetime import timedelta
from appointments.models import Appointment
from therapists.models import AvailableSlot
from twilio.rest import Client
from django.conf import settings

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
    interval = recurrence_map.get(recurring_appointment.recurrence_pattern, timedelta(weeks=1))

    # Start creating appointments
    current_date = recurring_appointment.start_date
    appointments = []

    for _ in range(recurring_appointment.number_of_occurrences):
        # Ensure therapist slot is available for this date
        day_name = current_date.strftime("%A").lower()
        available_slot = AvailableSlot.objects.filter(
            therapist=recurring_appointment.therapist,
            day=day_name,
            start_time=recurring_appointment.start_time
        ).exists()

        if not available_slot:
            current_date += interval
            continue

        # Prevent conflicts with existing appointments
        conflict = Appointment.objects.filter(
            therapist=recurring_appointment.therapist,
            date=current_date,
            start_time=recurring_appointment.start_time
        ).exists()

        if conflict:
            current_date += interval
            continue

        # Create the appointment if no conflicts
        appointments.append(Appointment(
            patient=recurring_appointment.patient,
            therapist=recurring_appointment.therapist,
            date=current_date,
            start_time=recurring_appointment.start_time,
            status='scheduled',
        ))

        # Move to the next occurrence
        current_date += interval

    # Bulk create appointments
    if appointments:
        Appointment.objects.bulk_create(appointments)
    else:
        print("No valid appointments could be scheduled")


def send_sms_notification(contact_number, recipient_name, requester_name, requested_date=None, requested_time=None, is_therapist=False, status=None, reason="No reason provided"):
    """ Sends an SMS notification via Twilio """
    message_body = None  # Initialize message body as None

    if status == "approved":
        message_body = (
            f"Hello {recipient_name}, your appointment on {requested_date} at {requested_time} has been APPROVED. "
            f"Please arrive on time."
        )
    elif status == "declined":
        message_body = (
            f"Hello {recipient_name},\n\n"
            f"Unfortunately, your appointment request on {requested_date} at {requested_time} has been *DECLINED**. "
            f"We apologize for any inconvenience.\n\n"
            f"To book another appointment, please follow these steps:\n"
            f"1. **Visit our appointment booking page**: [Appointment Request Page](https://o4p-deploy-test.onrender.com).\n"
            f"2. **Select a therapist** from the available list.\n"
            f"3. **Choose a new date and time** that fits your schedule.\n"
            f"4. **Submit your request**, and you will receive a confirmation once it is reviewed.\n\n"
            f"If you need any assistance, feel free to contact us.\n\n"
            f"We appreciate your understanding and look forward to assisting you.\n\n"
            f"Best regards,\n"
            f"[Therapro Therapy Clinic]"
        )

    elif status == "reschedule_request":
        message_body = (
            f"Hello {recipient_name}, {requester_name} has requested to reschedule their appointment to {requested_date} at {requested_time}. "
            f"Please review and approve it."
        )

    elif status == "cancelled":
        message_body = (
            f"Hello {recipient_name}, your appointment with {requester_name} on {requested_date} at {requested_time} has been CANCELLED. "
            f"Reason: {reason}."
        )
    
    elif is_therapist and status == "pending":
        message_body = (
            f"Hello {recipient_name}, you have a new appointment request from {requester_name} "
            f"on {requested_date} at {requested_time}. Please review and approve it."
        )
    elif not is_therapist and status == "pending":
        message_body = (
            f"Hello {recipient_name}, your appointment request with {requester_name} "
            f"on {requested_date} at {requested_time} has been submitted and is pending approval."
        )

    # Check if message_body is set; if not, print a debug message instead of sending an SMS
    if message_body:
        try:
            client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

            message = client.messages.create(
                body=message_body,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=contact_number
            )

            print(f"SMS sent successfully to {contact_number}. Message SID: {message.sid}")

        except Exception as e:
            print(f"Failed to send SMS to {contact_number}: {e}")
    else:
        print(f"No valid status provided. No SMS sent for {recipient_name} with status: {status}")