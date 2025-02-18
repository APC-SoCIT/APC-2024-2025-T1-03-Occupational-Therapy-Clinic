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
from accounts.models import GuardianInformation as Guardian
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
    # ✅ Fetch only therapist ID, ensuring `province_id` is not included
    therapist = get_object_or_404(
        Therapist.objects.only("id").defer("province_id"),  # ✅ Exclude province_id
        account_id=request.user.id
    )
    therapist_id = therapist.id  # ✅ Extract therapist ID directly

    # ✅ Fetch patients and pre-load them to avoid cursor issues
    patients = list(Patient.objects.values("id", "first_name", "last_name"))

    print("✅ Patients List:", patients)  # Debugging log

    form = AppointmentForm()

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            # ✅ Assign therapist_id instead of therapist object
            Appointment.objects.create(
                therapist_id=therapist_id,  # ✅ Use therapist_id directly
                patient=form.cleaned_data["patient"],  # ✅ Assign patient directly
                date=form.cleaned_data["date"],
                start_time=form.cleaned_data["start_time"],
                status="scheduled",
            )

            print("✅ New Appointment Created!")
            return redirect('appointment_list')

    return render(request, 'appointments/appointments/create_appointment.html', {
        'form': form,
        'therapist_id': therapist_id,  # ✅ Use `therapist_id` instead of the object
        'patients': patients  # ✅ Preloaded patient list
    })




def appointment_success(request):
    return render(request, 'appointments/appointments/appointment_success.html')

# Update Appointment (Therapists only)
@login_required
def update_appointment(request, appointment_id):
    appointment = get_object_or_404(
        Appointment.objects.select_related("therapist", "patient").values(
            "id", "patient_id", "patient__first_name", "patient__last_name", "first_name", "last_name",  # ✅ Include non-registered patient's name
            "therapist_id", "therapist__first_name", "date", "start_time", "status"
        ), id=appointment_id
    )

    authorized = False  # Default to unauthorized
    user = request.user

    # ✅ Check if user is a therapist
    if user.groups.filter(name='Therapist').exists():
        therapist = get_object_or_404(Therapist.objects.only("id"), account_id=user.id)
        if appointment["therapist_id"] == therapist.id:
            authorized = "therapist"

    # ✅ Check if user is a guardian of the patient
    elif user.groups.filter(name='Guardian').exists() and appointment["patient_id"]:
        patient = get_object_or_404(Patient.objects.only("id", "account_id"), id=appointment["patient_id"])
        if patient.account_id == user.id:
            authorized = "guardian"

    if request.method == 'POST':
        print("✅ Form Submitted!")  # Debugging

        new_date = request.POST.get("date")
        new_time = request.POST.get("start_time")

        print(f"📅 Submitted Date: {new_date}")  # Debugging
        print(f"🕒 Submitted Time: {new_time}")  # Debugging

        if not new_date or not new_time:
            messages.error(request, "⚠️ Please select a valid date and time.")
            return redirect(request.path)  # Stay on the same page if data is missing
        
        if authorized == "therapist":
            # ✅ Update appointment using `update()` (because `appointment` is a dictionary)
            Appointment.objects.filter(id=appointment_id).update(
                date=new_date,
                start_time=new_time
            )
            print("✅ Appointment Updated!")  # Debugging

            messages.success(request, "Appointment successfully updated!")
            return redirect('appointment_list')


        else:
            # ✅ Guardians request reschedule (Therapist must approve)
            therapist = get_object_or_404(Therapist, id=appointment["therapist_id"])
            AppointmentRequest.objects.create(
                first_name=appointment["patient__first_name"] if appointment["patient_id"] else appointment["first_name"],
                last_name=appointment["patient__last_name"] if appointment["patient_id"] else appointment["last_name"],
                contact_number=appointment.get("patient__contact_number", "N/A"),
                therapist=therapist,
                requested_date=new_date,
                requested_time=new_time,
                original_date=appointment["date"],  # ✅ Store original date
                original_time=appointment["start_time"],  # ✅ Store original start time
                status="pending"
            )
            print("✅ Reschedule Request Created!")  # Debugging

            messages.success(request, "Your reschedule request has been sent for therapist approval.")
            return redirect('appointment_list')

    return render(request, 'appointments/appointments/update_appointment.html', {
        'appointment': appointment,
        'therapist_id': appointment["therapist_id"],
        'authorized': authorized
    })



# Delete Appointment (Therapists only)
@login_required
def delete_appointment(request, appointment_id):  # ✅ Match URL parameter
    appointment = get_object_or_404(Appointment, id=appointment_id)

    # ✅ Ensure the user is a therapist
    therapist = get_object_or_404(Therapist.objects.only("id"), account_id=request.user.id)

    if appointment.therapist_id != therapist.id:
        messages.error(request, "You are not authorized to delete this appointment.")
        return render(request, '403.html', status=403)  # 🚫 Deny unauthorized access

    if request.method == 'POST':
        appointment.delete()
        messages.success(request, "Appointment successfully deleted.")
        return redirect('appointment_list')

    return render(request, 'appointments/appointments/confirm_delete.html', {'appointment': appointment})




@login_required
def appointment_list(request):
    user = request.user

    # ✅ Assistants: See all appointments
    if user.groups.filter(name='Assistant').exists():
        appointments = Appointment.objects.select_related("patient").order_by("date", "start_time")

    # ✅ Therapists: See only their appointments
    elif user.groups.filter(name='Therapist').exists():
        therapist = Therapist.objects.only("id").get(account_id=user)  # ✅ Get therapist instance
        appointments = Appointment.objects.select_related("patient").filter(therapist=therapist).order_by("date", "start_time")

    # ✅ Guardians: See their patients' appointments
    elif user.groups.filter(name="Guardian").exists():
        guardian_patient_ids = list(Patient.objects.filter(account_id=user.id).values_list("id", flat=True))
        appointments = Appointment.objects.select_related("patient").filter(patient_id__in=guardian_patient_ids)


    else:
        appointments = Appointment.objects.none()


    return render(request, 'appointments/appointments/appointment_list.html', {'appointments': appointments})



@login_required
def appointment_detail(request, appointment_id):
    # ✅ Fetch only necessary fields to prevent errors
    appointment = get_object_or_404(
        Appointment.objects.select_related("therapist", "patient").values(
            "id", "patient_id", "patient__first_name", "patient__last_name", "first_name", "last_name",  # ✅ Include non-registered patient's name
            "therapist_id", "therapist__first_name", 
            "date", "start_time", "status"
        ), id=appointment_id
    )

    user = request.user

    # ✅ Allow therapists to view their assigned appointments
    if user.groups.filter(name='Therapist').exists():
        therapist = Therapist.objects.only("id").get(account_id=user)
        if appointment["therapist_id"] == therapist.id:
            return render(request, 'appointments/appointments/appointment_detail.html', {'appointment': appointment})

    # ✅ Allow assistants to view appointments
    elif user.groups.filter(name='Assistant').exists() and appointment["patient_id"]:
        patient = Patient.objects.only("id").get(id=appointment["patient_id"])
        if patient.account_id == user:
            return render(request, 'appointments/appointments/appointment_detail.html', {'appointment': appointment})

    # ✅ Allow guardians to view appointments of their patients
    elif user.groups.filter(name='Guardian').exists() and appointment["patient_id"]:
        patient = get_object_or_404(Patient.objects.only("id", "account_id"), id=appointment["patient_id"])
        if patient.account_id == user:
            return render(request, 'appointments/appointments/appointment_detail.html', {'appointment': appointment})

    # 🚫 Deny access if user is not related to the appointment
    return render(request, '403.html', status=403)



# Create Appointment Request (For Non-Registered Users)
def create_appointment_request(request):
    # ✅ Fetch therapists correctly
    therapists = Therapist.objects.values("id", "first_name", "last_name")

    print("📡 Django Sending These Therapists:", list(therapists))  # ✅ Debugging

    if request.method == 'POST':
        form = AppointmentRequestForm(request.POST)

        print("Form submitted with:", request.POST)  # ✅ Debugging log

        if form.is_valid():
            therapist = form.cleaned_data['therapist']  # ✅ Correct therapist instance

            requested_date = form.cleaned_data['requested_date']
            requested_time = form.cleaned_data['requested_time']

            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            contact_number = form.cleaned_data['contact_number']
            notes = form.cleaned_data['notes']

            print("Valid form. Requested time:", requested_time)  # ✅ Debugging log
            print("Form Data:", form.cleaned_data)

            # ✅ Check if the slot already has 3 requests
            existing_requests = AppointmentRequest.objects.filter(
                therapist=therapist,
                requested_date=requested_date,
                requested_time=requested_time,
                status='pending'
            ).count()

            if existing_requests >= 3:
                messages.error(request, "This time slot has reached its request limit. Please choose another time.")
                return redirect('create_appointment_request')

            # ✅ Save appointment request with the correct therapist instance
            appointment_request = AppointmentRequest.objects.create(
                first_name=first_name,
                last_name=last_name,
                contact_number=contact_number,
                therapist=therapist,  # ✅ Assign TherapistInformation instance
                requested_date=requested_date,
                requested_time=requested_time,
                notes=notes,
                status='pending'
            )

            print("✅ Appointment request successfully saved:", appointment_request)
            messages.success(request, "Your appointment request has been submitted and is pending approval.")
            return redirect('request_success')
        else:
            print("❌ Form Errors:", form.errors)  # ✅ Debugging: Print errors if form is invalid

    else:
        form = AppointmentRequestForm()

    return render(request, 'appointments/requests/create_appointment_request.html', {
        'form': form,
        'therapists': therapists  # ✅ Pass only necessary fields
    })



@login_required
@user_passes_test(lambda user: user.groups.filter(name='Therapist').exists())
def manage_appointment_requests(request):
    therapist = Therapist.objects.only("id").get(account_id=request.user)


    # Fetch only pending appointment requests for this therapist
    requests = AppointmentRequest.objects.filter(status='pending', therapist=therapist)
    
    return render(request, 'appointments/requests/appointment_requests.html', {'requests': requests})




# Update Appointment Request Status
@login_required
def update_request_status(request, request_id):
    therapist = get_object_or_404(Therapist.objects.only("id"), account_id=request.user.id)
    appointment_request = get_object_or_404(AppointmentRequest, id=request_id, therapist=therapist)

    if request.method == 'POST':
        new_status = request.POST.get('status')
        appointment_request.status = new_status
        appointment_request.save()

        if new_status == 'approved':
            existing_patient = Patient.objects.only("id").filter(
                first_name=appointment_request.first_name,
                last_name=appointment_request.last_name
            ).first()

            # ✅ Ensure we delete the exact previous scheduled appointment
            old_appointment_query = Appointment.objects.filter(
                therapist=appointment_request.therapist,
                patient=existing_patient if existing_patient else None,
                date=appointment_request.original_date,  # ✅ Match the original date before rescheduling
                start_time=appointment_request.original_time,  # ✅ Match the exact time before rescheduling
                status="scheduled"
            )

            print(f"🔍 Querying for old appointment: {old_appointment_query.query}")

            old_appointment = old_appointment_query.first()

            if old_appointment:
                print(f"🗑️ Deleting previous appointment: {old_appointment.id} on {old_appointment.date} at {old_appointment.start_time}")
                old_appointment.delete()
            else:
                print("⚠️ No exact match for previous appointment found. Skipping deletion.")

            # ✅ Create the new rescheduled appointment
            Appointment.objects.create(
                therapist=appointment_request.therapist,
                patient=existing_patient if existing_patient else None,
                first_name=appointment_request.first_name,
                last_name=appointment_request.last_name,
                date=appointment_request.requested_date,
                start_time=appointment_request.requested_time,
                status='scheduled',
            )

            messages.success(request, "Appointment rescheduled successfully. The previous appointment has been removed.")

        return redirect('manage_appointment_requests')

    return render(request, 'appointments/requests/update_request_status.html', {'appointment_request': appointment_request})




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



# ✅ Function to convert weekday name (e.g., "monday") to actual date
def get_next_date_from_weekday(weekday_name):
    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    today = datetime.today().date()
    
    if weekday_name.lower() not in weekdays:
        return None  # Return None if invalid weekday name
    
    weekday_index = weekdays.index(weekday_name.lower())
    days_ahead = (weekday_index - today.weekday()) % 7
    return today + timedelta(days=days_ahead)

@login_required
def appointments_calendar_api(request):
    start = request.GET.get("start")
    end = request.GET.get("end")
    therapist_id = request.GET.get("therapist_id")
    user = request.user

    if not start or not end:
        return JsonResponse({"error": "Start and end dates are required"}, status=400)

    start_date = datetime.fromisoformat(start).date()
    end_date = datetime.fromisoformat(end).date()

    # ✅ Determine user role and filter accordingly
    filter_criteria = {}

    if user.groups.filter(name="Therapist").exists():
        filter_criteria["therapist_id"] = therapist_id

    elif user.groups.filter(name="Guardian").exists():
        guardian_patient_ids = request.GET.get("guardian_patient_ids", "").split(",")
        guardian_patient_ids = [int(pid) for pid in guardian_patient_ids if pid.isdigit()]  # ✅ Convert to integers
        if guardian_patient_ids:
            filter_criteria["patient_id__in"] = guardian_patient_ids



    # ✅ Fetch scheduled appointments based on role
    appointments = Appointment.objects.filter(
        **filter_criteria,
        date__range=(start_date, end_date),
        status="scheduled"
    ).select_related("patient").values(
        "id", "date", "start_time", "status",
        "patient__first_name", "patient__last_name",
        "first_name", "last_name"
    ).order_by("date", "start_time")

    # ✅ Format booked appointments for the calendar
    booked_events = [
        {
            "title": f"📅 {appt['date']} | 🕒 {appt['start_time']} | 👤 {appt['patient__first_name'] or appt['first_name']} {appt['patient__last_name'] or appt['last_name']}",
            "start": datetime.combine(appt["date"], appt["start_time"]).isoformat(),
            "end": (datetime.combine(appt["date"], appt["start_time"]) + timedelta(hours=1)).isoformat(),
            "color": "#808080",
            "extendedProps": {
                "status": "booked",
                "patient_name": f"{appt['patient__first_name'] or appt['first_name']} {appt['patient__last_name'] or appt['last_name']}"
            }
        }
        for appt in appointments
    ]

    return JsonResponse(booked_events, safe=False)
    
@login_required
def calendar_view(request):
    user = request.user
    therapist_id = None
    guardian_patient_ids = []  # ✅ Store IDs of patients assigned to the Guardian

    if user.groups.filter(name="Therapist").exists():
        therapist = Therapist.objects.filter(account_id=user.id).values("id").first()
        therapist_id = therapist["id"] if therapist else None  # ✅ Set therapist_id

    elif user.groups.filter(name="Guardian").exists():
        guardian_patient_ids = list(Patient.objects.filter(account_id=user.id).values_list("id", flat=True))


    return render(request, "appointments/calendar.html", {
        "therapist_id": therapist_id,
        "guardian_patient_ids": ",".join(map(str, guardian_patient_ids)),  # ✅ Convert to comma-separated string for JavaScript
        "user_role": user.groups.first().name
    })


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