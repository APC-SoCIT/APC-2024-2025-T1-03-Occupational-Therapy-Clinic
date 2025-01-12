from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db import transaction
import json
from openai import PermissionDeniedError
from .models import NonWorkingDay
from .models import Appointment
from .models import AppointmentRequest
from .models import AppointmentSlot
from .models import RecurringAppointment
from .forms import AppointmentForm
from .forms import RecurringAppointmentForm
from .forms import AppointmentRequestForm
from .utils import generate_recurring_appointments
from datetime import datetime, timedelta

# Check if the user is in the Therapist group
def is_therapist(user):
    return user.groups.filter(name="Therapist").exists()

# Check if the user is in the Patient group
def is_patient(user):
    return user.groups.filter(name="Patient").exists()

# Create Appointment (Therapists only)
@login_required
@user_passes_test(is_therapist)
def create_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'appointments/appointments/appointment_success.html')
    else:
        form = AppointmentForm()
    return render(request, 'appointments/appointments/create_appointment.html', {'form': form})

def appointment_success(request):
    return render(request, 'appointments/appointments/appointment_success.html')

# Update Appointment (Therapists only)
@login_required
@user_passes_test(is_therapist)
def update_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk, therapist=request.user)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            return redirect('appointment_list')
    else:
        form = AppointmentForm(instance=appointment)
    return render(request, 'appointments/appointments/update_appointment.html', {'form': form, 'appointment': appointment})

# Delete Appointment (Therapists only)
@login_required
@user_passes_test(is_therapist)
def delete_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk, therapist=request.user)
    if request.method == 'POST':
        appointment.delete()
        return redirect('appointment_list')
    return render(request, 'appointments/appointments/delete_appointment.html', {'appointment': appointment})

@login_required
def appointment_list(request):
    user = request.user

    if user.groups.filter(name='Therapist').exists():
        # Therapist: Show appointments where they are the therapist
        appointments = Appointment.objects.filter(therapist=user)
    elif user.groups.filter(name='Patient').exists():
        # Patient: Show appointments where they are the patient
        appointments = Appointment.objects.filter(patient=user)
    else:
        appointments = Appointment.objects.none()

    return render(request, 'appointments/appointments/appointment_list.html', {'appointments': appointments})

@login_required
def appointment_detail(request, pk):
    # Fetch the appointment if the logged-in user has access to it
    appointment = get_object_or_404(Appointment, pk=pk)

    # Ensure the user is authorized to view this appointment
    if request.user != appointment.patient and request.user != appointment.therapist:
        raise PermissionDeniedError

    return render(request, 'appointments/appointments/appointment_detail.html', {'appointment': appointment})

def create_appointment_request(request):
    if request.method == 'POST':
        therapist_id = request.POST.get('therapist')
        requested_date = request.POST.get('requested_date')
        requested_time = request.POST.get('requested_time')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        contact_number = request.POST.get('contact_number')
        notes = request.POST.get('notes')

        therapist = get_object_or_404(User, id=therapist_id, groups__name="Therapist")
        AppointmentRequest.objects.create(
            first_name=first_name,
            last_name=last_name,
            contact_number=contact_number,
            therapist=therapist,
            requested_date=requested_date,
            requested_time=requested_time,
            notes=notes,
        )
        return redirect('request_success')

    therapists = User.objects.filter(groups__name="Therapist")
    return render(request, 'appointments/requests/create_appointment_request.html', {'therapists': therapists})


# View and Manage Appointment Requests (Therapist)
login_required
@user_passes_test(lambda user: user.groups.filter(name='Therapist').exists())
def manage_appointment_requests(request):
    # Fetch only pending appointment requests
    requests = AppointmentRequest.objects.filter(status='pending', therapist=request.user)
    return render(request, 'appointments/requests/appointment_requests.html', {'requests': requests})

# Update Appointment Request Status
@login_required
@user_passes_test(lambda user: user.groups.filter(name='Therapist').exists())
def update_request_status(request, request_id):
    appointment_request = get_object_or_404(AppointmentRequest, id=request_id, therapist=request.user)
    if request.method == 'POST':
        new_status = request.POST.get('status')

        # Update the AppointmentRequest status
        appointment_request.status = new_status
        appointment_request.save()

        # If approved, create a new Appointment
        if new_status == 'approved':
            # Try to find an existing patient User instance
            patient_user = User.objects.filter(
                first_name=appointment_request.first_name,
                last_name=appointment_request.last_name,
            ).first()

            if not patient_user:
                # Handle the case for non-account patients
                patient_user = User.objects.create(
                    username=f"{appointment_request.first_name.lower()}_{appointment_request.last_name.lower()}_{appointment_request.id}",
                    first_name=appointment_request.first_name,
                    last_name=appointment_request.last_name,
                    is_active=False,  # Ensure this account cannot be used for login
                )

            # Create the appointment
            Appointment.objects.create(
                patient=patient_user,
                therapist=appointment_request.therapist,
                date=appointment_request.requested_date,
                start_time=appointment_request.requested_time,
                status='scheduled',
            )

        return redirect('manage_appointment_requests')

def request_success(request):
    return render(request, 'appointments/requests/request_success.html')

@login_required
@user_passes_test(is_therapist)
def create_recurring_appointment(request):
    if request.method == 'POST':
        form = RecurringAppointmentForm(request.POST)
        if form.is_valid():
            recurring_appointment = form.save()
            try:
                generate_recurring_appointments(recurring_appointment)  # Generate appointments
                messages.success(request, "Recurring appointments scheduled successfully!")
                return redirect('therapist_dashboard')
            except ValueError as e:
                # Handle conflicts
                messages.error(request, str(e))
                recurring_appointment.delete()  # Clean up incomplete data
        else:
            messages.error(request, "Invalid form submission.")
    else:
        form = RecurringAppointmentForm()
    return render(request, 'appointments/recurring/create_recurring_appointment.html', {'form': form})



@login_required
def appointments_calendar_api(request):
    start = request.GET.get('start')  # Start date in ISO format
    end = request.GET.get('end')  # End date in ISO format

    # Parse the start and end dates (if they exist)
    start_date = datetime.fromisoformat(start).date() if start else None
    end_date = datetime.fromisoformat(end).date() if end else None

    # Query appointments within the date range
    if start_date and end_date:
        appointments = Appointment.objects.filter(date__range=(start_date, end_date))
    else:
        appointments = Appointment.objects.all()

    # Get the logged-in user
    user = request.user

        # Filter appointments based on user role
    if user.groups.filter(name='Therapist').exists():
        appointments = Appointment.objects.filter(
            therapist=user,
            date__range=(start_date, end_date) if start_date and end_date else None,
        )
    elif user.groups.filter(name='Patient').exists():
        appointments = Appointment.objects.filter(
            patient=user,
            date__range=(start_date, end_date) if start_date and end_date else None,
        )
    else:
        appointments = Appointment.objects.none()  # No appointments for other roles

    # Format the events for FullCalendar
    events = [
        {
            "title": f"Session with {appt.patient.username}",
            "start": datetime.combine(appt.date, appt.start_time).isoformat(),
            "end": (datetime.combine(appt.date, appt.start_time) + timedelta(hours=1)).isoformat(),
            "url": f"/appointment/{appt.id}"  # Optional: URL for event details
        }
        for appt in appointments
    ]

    return JsonResponse(events, safe=False)

    
def calendar_view(request):
    """Render the calendar interface."""
    return render(request, 'appointments/calendar.html')


def get_non_working_days(request):
    therapist_id = request.GET.get('therapist_id')
    non_working_days = NonWorkingDay.objects.filter(therapist_id=therapist_id).values_list('date', flat=True)
    return JsonResponse({'non_working_days': list(non_working_days)})

def get_available_slots(request):
    # Extract date from the request
    selected_date = request.GET.get('date')

    if not selected_date:
        return JsonResponse({"error": "Date is required."}, status=400)

    # Define working hours (example: 9 AM to 5 PM)
    working_hours = [
        (9, 0), (10, 0), (11, 0), (12, 0), (13, 0),
        (14, 0), (15, 0), (16, 0), (17, 0)
    ]

    # Check appointments for the selected date
    appointments = Appointment.objects.filter(date__date=selected_date)
    booked_slots = {appt.date.strftime("%H:%M") for appt in appointments}

    # Generate available slots
    available_slots = []
    for hour, minute in working_hours:
        slot_time = f"{hour:02}:{minute:02}"
        if slot_time not in booked_slots:
            available_slots.append(f"{hour:02}:{minute:02}")

    return JsonResponse({"slots": available_slots})

@login_required
def patient_appointments(request):
    # Ensure the user is in the 'Patient' group
    if not request.user.groups.filter(name="Patient").exists():
        return JsonResponse({"error": "Unauthorized"}, status=403)
    
    # Fetch appointments assigned to the logged-in patient
    appointments = Appointment.objects.filter(patient=request.user)
    
    # Serialize data for FullCalendar
    events = [
        {
            "title": f"Therapist: {appt.therapist.username}",
            "start": f"{appt.date}T{appt.start_time}",
            "end": f"{appt.date}T{appt.end_time}",
            "status": appt.status,
        }
        for appt in appointments
    ]
    return JsonResponse(events, safe=False)

@login_required
def therapist_appointments(request):
    # Ensure the user is in the 'Therapist' group
    if not request.user.groups.filter(name="Therapist").exists():
        return JsonResponse({"error": "Unauthorized"}, status=403)
    
    # Fetch appointments assigned to the logged-in therapist
    appointments = Appointment.objects.filter(therapist=request.user)
    
    # Serialize data for FullCalendar
    events = [
        {
            "title": f"Patient: {appt.patient.username}",
            "start": f"{appt.date}T{appt.start_time}",
            "end": f"{appt.date}T{appt.end_time}",
            "status": appt.status,
        }
        for appt in appointments
    ]
    return JsonResponse(events, safe=False)