from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.models import Group  # Import Django's Group model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db import transaction
from django.db.models import F
import json
from django.core.exceptions import PermissionDenied
from django.core.exceptions import ObjectDoesNotExist
from .models import Appointment, RecurringAppointment, AppointmentRequest
from therapists.models import AvailableSlot
from accounts.models import TherapistInformation as Therapist
from patients.models import PatientInformation as Patient
from .forms import AppointmentForm
from .forms import RecurringAppointmentForm
from .forms import AppointmentRequestForm
from .utils import generate_recurring_appointments
from datetime import datetime, timedelta, date
import calendar
import traceback


# Create Appointment (Therapists only)
@login_required
def create_appointment(request):
    try:
        therapist = Therapist.objects.get(account_id=request.user)  # ✅ Fetch therapist correctly
    except Therapist.DoesNotExist:
        return render(request, '403.html', status=403)  # 🚫 Not a valid therapist

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.therapist = therapist  # ✅ Ensure the logged-in therapist is assigned
            appointment.save()
            return redirect('appointment_list')
    else:
        form = AppointmentForm()

    return render(request, 'appointments/appointments/create_appointment.html', {
        'form': form,
        'therapist_id': therapist.id  # ✅ Pass therapist_id to template
        })

def appointment_success(request):
    return render(request, 'appointments/appointments/appointment_success.html')

# Update Appointment (Therapists only)
@login_required
def update_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk)

    authorized = False  # Default to unauthorized

    # ✅ Check if user is a therapist
    if request.user.groups.filter(name='Therapist').exists():
        therapist = get_object_or_404(Therapist, account_id=request.user)  # ✅ Ensure therapist exists
        if appointment.therapist == therapist:
            authorized = "therapist"

    # ✅ Check if user is a guardian of the patient
    elif request.user.groups.filter(name='Guardian').exists():
        if appointment.patient and appointment.patient.account_id == request.user:
            authorized = "guardian"

    if not authorized:
        messages.error(request, "You are not authorized to update this appointment.")
        return render(request, '403.html', status=403)  # 🚫 Deny unauthorized access

    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)

        if form.is_valid():
            if authorized == "therapist":
                form.save()  # ✅ Therapists can update directly
                updated_appointment = get_object_or_404(Appointment, pk=pk)
                print(f"✅ Appointment After Save: {updated_appointment.__dict__}")  # ✅ Debugging
                return redirect('appointment_list')
            else:
                # ✅ Convert guardian updates into an appointment request
                AppointmentRequest.objects.create(
                    first_name=appointment.patient.first_name if appointment.patient else "Unknown",
                    last_name=appointment.patient.last_name if appointment.patient else "Unknown",
                    contact_number=appointment.patient.contact_number if appointment.patient else "N/A",
                    therapist=appointment.therapist,
                    requested_date=form.cleaned_data["date"],
                    requested_time=form.cleaned_data["start_time"],
                    status="pending"
                )
                messages.success(request, "Your reschedule request has been sent for therapist approval.")

            return redirect('appointment_list')

    else:
        form = AppointmentForm(instance=appointment)

    return render(request, 'appointments/appointments/update_appointment.html', {
        'form': form,
        'appointment': appointment,
        'therapist_id': therapist.id,
        'authorized': authorized  # ✅ Pass authorization status to template
    })
# Delete Appointment (Therapists only)
@login_required

def delete_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk, therapist=request.user)
    if request.method == 'POST':
        appointment.delete()
        return redirect('appointment_list')
    return render(request, 'appointments/appointments/delete_appointment.html', {'appointment': appointment})

@login_required
def appointment_list(request):
    user = request.user

    # ✅ Assistants: See all appointments
    if user.groups.filter(name='Assistant').exists():
        appointments = Appointment.objects.all()

    # ✅ Therapists: See only their appointments
    elif user.groups.filter(name='Therapist').exists():
        therapist = Therapist.objects.get(account_id=user)  # ✅ Get therapist instance
        appointments = Appointment.objects.filter(therapist=therapist)

    # ✅ Guardians: See their patients' appointments
    elif user.groups.filter(name='Guardian').exists():
        patients = Patient.objects.filter(guardian=user)  # ✅ Get all their patients
        appointments = Appointment.objects.filter(patient__in=patients)
    else:
        appointments = Appointment.objects.none()

    return render(request, 'appointments/appointments/appointment_list.html', {'appointments': appointments})


@login_required
def appointment_detail(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # ✅ Allow therapists to view their assigned appointments
    if request.user.groups.filter(name='Therapist').exists():
        therapist = Therapist.objects.get(account_id=request.user)
        if appointment.therapist == therapist:
            return render(request, 'appointments/appointments/appointment_detail.html', {'appointment': appointment})

    # ✅ Allow patients to view their own appointments
    if request.user.groups.filter(name='Patient').exists():
        patient = Patient.objects.get(account_id=request.user)
        if appointment.patient == patient:
            return render(request, 'appointments/appointments/appointment_detail.html', {'appointment': appointment})

    # ✅ Allow guardians to view appointments of their patients
    if request.user.groups.filter(name='Guardian').exists():
        patient = appointment.patient
        if patient and patient.account_id == request.user:
            return render(request, 'appointments/appointments/appointment_detail.html', {'appointment': appointment})

    # 🚫 Deny access if user is not related to the appointment
    return render(request, '403.html', status=403)


# Create Appointment Request (For Non-Registered Users)
def create_appointment_request(request):
    therapists = Therapist.objects.all()
    print("📡 Django Sending These Therapists:", therapists.values("id", "first_name", "last_name"))  # ✅ Debugging

    if request.method == 'POST':
        form = AppointmentRequestForm(request.POST)

        print("Form submitted with:", request.POST)  # Debugging log

        if form.is_valid():
            therapist = form.cleaned_data['therapist']  # This is a User instance

            requested_date = form.cleaned_data['requested_date']
            requested_time = form.cleaned_data['requested_time']

            print("Valid form. Requested time:", requested_time)  # Debugging log

            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            contact_number = form.cleaned_data['contact_number']
            notes = form.cleaned_data['notes']

            # Debugging: Print form data to check values before saving
            print("Form Data:", form.cleaned_data)

            # Count existing requests for this slot
            existing_requests = AppointmentRequest.objects.filter(
                therapist=therapist,
                requested_date=requested_date,
                requested_time=requested_time,
                status='pending'
            ).count()

            if existing_requests >= 3:
                messages.error(request, "This time slot has reached its request limit. Please choose another time.")
                return redirect('create_appointment_request')

            # Save appointment request
            appointment_request = AppointmentRequest.objects.create(
                first_name=first_name,
                last_name=last_name,
                contact_number=contact_number,
                therapist=therapist,  # Assigning a User instance instead of a Therapist instance
                requested_date=requested_date,
                requested_time=requested_time,
                notes=notes,
                status='pending'
            )

            print("Appointment request successfully saved:", appointment_request)
            messages.success(request, "Your appointment request has been submitted and is pending approval.")
            return redirect('request_success')
        else:
            print("Form Errors:", form.errors)  # Debugging: Print errors if form is invalid

    else:
        form = AppointmentRequestForm()

    return render(request, 'appointments/requests/create_appointment_request.html', {
        'form': form,
        'therapists': therapists
    })



@login_required
@user_passes_test(lambda user: user.groups.filter(name='Therapist').exists())
def manage_appointment_requests(request):
    therapist = Therapist.objects.get(account_id=request.user)  # ✅ Fix therapist lookup

    # Fetch only pending appointment requests for this therapist
    requests = AppointmentRequest.objects.filter(status='pending', therapist=therapist)
    
    return render(request, 'appointments/requests/appointment_requests.html', {'requests': requests})




# Update Appointment Request Status
@login_required
def update_request_status(request, request_id):
    therapist = Therapist.objects.get(account_id=request.user)  # ✅ Get therapist instance
    appointment_request = get_object_or_404(AppointmentRequest, id=request_id, therapist=therapist)

    if request.method == 'POST':
        new_status = request.POST.get('status')

        # ✅ Update AppointmentRequest status
        appointment_request.status = new_status
        appointment_request.save()

        # ✅ If approved, create an appointment for non-registered users only
        if new_status == 'approved':
            existing_patient = Patient.objects.filter(
                first_name=appointment_request.first_name,
                last_name=appointment_request.last_name
            ).first()

            # ✅ Create the appointment
            Appointment.objects.create(
                therapist=appointment_request.therapist,
                date=appointment_request.requested_date,
                start_time=appointment_request.requested_time,
                status='scheduled',
            )

        return redirect('manage_appointment_requests')

def request_success(request):
    return render(request, 'appointments/requests/request_success.html')

@login_required
def create_recurring_appointment(request):
    if request.method == 'POST':
        form = RecurringAppointmentForm(request.POST)
        if form.is_valid():
            recurring_appointment = form.save()
            try:
                generate_recurring_appointments(recurring_appointment)  # Generate appointments
                messages.success(request, "Recurring appointments scheduled successfully!")
                return redirect('calendar_view')
            except ValueError as e:
                # Handle conflicts
                messages.error(request, str(e))
                recurring_appointment.delete()  # Clean up incomplete data
        else:
            messages.error(request, "Invalid form submission.")
    else:
        form = RecurringAppointmentForm()
    return render(request, 'appointments/recurring/create_recurring_appointment.html', {'form': form})



def appointments_calendar_api(request):
    start = request.GET.get('start')  # Start date in ISO format
    end = request.GET.get('end')  # End date in ISO format
    therapist_id = request.GET.get('therapist_id')
    user = request.user  # Get logged-in user
    
    start_date = datetime.fromisoformat(start).date() if start else None
    end_date = datetime.fromisoformat(end).date() if end else None

    # ✅ Show booked appointments to all users (including non-logged-in users)
    appointments = Appointment.objects.filter(date__range=(start_date, end_date))

    booked_events = [
        {
            "title": "Booked",
            "start": datetime.combine(appt.date, appt.start_time).isoformat(),
            "end": (datetime.combine(appt.date, appt.start_time) + timedelta(hours=1)).isoformat(),
            "color": "#808080",
            "extendedProps": {"status": "booked"}
        }
        for appt in appointments
    ]
    
    available_events = []
    if therapist_id:
        available_slots = AvailableSlot.objects.filter(therapist_id=therapist_id)
        for slot in available_slots:
             # ✅ Check if the slot is fully booked (3 bookings per slot max)
            booked_count = Appointment.objects.filter(
                therapist_id=therapist_id, date=slot.date, start_time=slot.start_time
            ).count()
            if booked_count < 3:  # ✅ Only show available slots if less than 3 bookings
                available_events.append({
                    "title": "Available",
                    "start": datetime.combine(slot.date, slot.start_time).isoformat(),
                    "end": datetime.combine(slot.date, slot.end_time).isoformat(),
                    "color": "#007BFF",
                    "extendedProps": {"status": "available"}
                })
        
    return JsonResponse(booked_events + available_events, safe=False)

    
def calendar_view(request):
    """Render the calendar interface."""
    return render(request, 'appointments/calendar.html')


def get_available_slots(request, therapist_id):
    requested_date = request.GET.get("date", None)
    print(f"📡 API received request for Therapist ID: {therapist_id} on {requested_date}")

    if not requested_date:
        return JsonResponse({"error": "Date parameter is required"}, status=400)

    try:
        # Convert requested date to weekday name
        day_name = datetime.strptime(requested_date, "%Y-%m-%d").strftime("%A").lower()
        
        # Fetch slots for the selected date and therapist's schedule
        slots = AvailableSlot.objects.filter(therapist_id=therapist_id, day=day_name).order_by("start_time")

        print(f"✅ Found {slots.count()} available slots for Therapist ID {therapist_id} on {requested_date}")
        
        if not slots.exists():
            return JsonResponse({"available_slots": []})  # Return empty if no slots available

        slot_data = []
        for slot in slots:
            # ✅ Check how many appointments are booked for this slot
            booked_count = Appointment.objects.filter(
                therapist_id=therapist_id, date=requested_date, start_time=slot.start_time
            ).count()

            if booked_count < 3:  # ✅ Only return slots with fewer than 3 appointments
                slot_data.append({
                    "date": requested_date,
                    "start_time": slot.start_time.strftime("%H:%M"),
                    "end_time": slot.end_time.strftime("%H:%M")
                })

        return JsonResponse({"available_slots": slot_data})

    except Exception as e:
        return JsonResponse({"error": "Internal server error", "details": str(e)}, status=500)