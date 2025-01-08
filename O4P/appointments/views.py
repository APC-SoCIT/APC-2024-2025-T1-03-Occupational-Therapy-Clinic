from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
import json
from .models import Appointment
from .models import AppointmentRequest
from .models import RecurringAppointment
from .forms import AppointmentForm
from .forms import RecurringAppointmentForm
from .utils import generate_recurring_appointments

# Check if the user is in the Therapist group
def is_therapist(user):
    return user.groups.filter(name="Therapist").exists()

# Check if the user is in the Patient group
def is_patient(user):
    return user.groups.filter(name="Patient").exists()

# Therapist Dashboard
class TherapistDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "appointments/therapist_dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        appointments = Appointment.objects.filter(therapist=self.request.user)
        # Add appointments as events for the calendar
        context['appointments'] = appointments
        context['events'] = [
            {
                "title": f"Appointment with {appt.patient.username}",
                "start": f"{appt.date}T{appt.start_time}",
            }
            for appt in appointments
        ]
        return context

# Patient Dashboard
@login_required
@user_passes_test(is_patient)
def patient_dashboard(request):
    appointments = Appointment.objects.filter(patient=request.user)
    return render(request, 'appointments/patient_dashboard.html', {'appointments': appointments})

# Create Appointment (Therapists only)
@login_required
@user_passes_test(is_therapist)
def create_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('therapist_dashboard')
    else:
        form = AppointmentForm()
    return render(request, 'appointments/create_appointment.html', {'form': form})

# Update Appointment (Therapists only)
@login_required
@user_passes_test(is_therapist)
def update_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk, therapist=request.user)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            return redirect('therapist_dashboard')
    else:
        form = AppointmentForm(instance=appointment)
    return render(request, 'appointments/update_appointment.html', {'form': form, 'appointment': appointment})

# Delete Appointment (Therapists only)
@login_required
@user_passes_test(is_therapist)
def delete_appointment(request, pk):
    appointment = get_object_or_404(Appointment, pk=pk, therapist=request.user)
    if request.method == 'POST':
        appointment.delete()
        return redirect('therapist_dashboard')
    return render(request, 'appointments/delete_appointment.html', {'appointment': appointment})


# Appointment list for therapists
@login_required
@user_passes_test(is_therapist)
def appointment_list(request):
    appointments = Appointment.objects.filter(therapist=request.user)
    return render(request, 'appointments/appointment_list.html', {'appointments': appointments})

# Appointment list for patients
@login_required
@user_passes_test(is_patient)
def patient_appointment_list(request):
    appointments = Appointment.objects.filter(patient=request.user)
    return render(request, 'appointments/appointment_list.html', {'appointments': appointments})

# Create Appointment Request (Patient)
@login_required
@user_passes_test(is_patient)
def create_appointment_request(request):
    if request.method == 'POST':
        therapist_id = request.POST.get('therapist')
        requested_date = request.POST.get('requested_date')
        requested_time = request.POST.get('requested_time')
        notes = request.POST.get('notes')
        
        therapist = get_object_or_404(User, id=therapist_id, groups__name="Therapist")
        AppointmentRequest.objects.create(
            patient=request.user,
            therapist=therapist,
            requested_date=requested_date,
            requested_time=requested_time,
            notes=notes
        )
        return redirect('patient_dashboard')
    
    therapists = User.objects.filter(groups__name="Therapist")
    return render(request, 'appointments/create_appointment_request.html', {'therapists': therapists})

# View and Manage Appointment Requests (Therapist)
@login_required
@user_passes_test(lambda user: user.groups.filter(name='Therapist').exists())
def manage_appointment_requests(request):
    # Show only pending appointment requests
    appointment_requests = AppointmentRequest.objects.filter(therapist=request.user, status='pending')
    return render(request, 'appointments/appointment_requests.html', {'appointment_requests': appointment_requests})

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
            Appointment.objects.create(
                patient=appointment_request.patient,
                therapist=appointment_request.therapist,
                date=appointment_request.requested_date,
                start_time=appointment_request.requested_time,
                status='scheduled'
            )

        return redirect('manage_appointment_requests')
    

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
            Appointment.objects.create(
                patient=appointment_request.patient,
                therapist=appointment_request.therapist,
                date=appointment_request.requested_date,
                start_time=appointment_request.requested_time,
                status='scheduled'
            )

        return redirect('manage_appointment_requests')
    
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
    return render(request, 'appointments/create_recurring_appointment.html', {'form': form})



def appointments_calendar_api(request):
    """API to fetch appointments for FullCalendar."""
    if request.method == 'GET':
        appointments = Appointment.objects.all()
        events = [
            {
                'title': f"{appointment.patient.username} with {appointment.therapist.username}",
                'start': f"{appointment.date}T{appointment.start_time}",
                'end': f"{appointment.date}T{appointment.end_time}",
                'id': appointment.id,
            }
            for appointment in appointments
        ]
        return JsonResponse(events, safe=False)
    
@csrf_exempt
def create_appointment_api(request):
    """API to handle creating new appointments."""
    if request.method == 'POST':
        data = json.loads(request.body)
        date = data.get('date')
        details = data.get('details')

        # Replace with actual user objects
        therapist = request.user  # Example: logged-in user as therapist
        patient = request.user  # Replace with logic for selecting patient

        Appointment.objects.create(
            patient=patient,
            therapist=therapist,
            date=date,
            start_time='09:00',  # Example fixed time
            end_time='10:00',    # Example fixed duration
            status='scheduled',
        )
        return JsonResponse({'message': 'Appointment created successfully!'}, status=201)
    
def calendar_view(request):
    """Render the calendar interface."""
    return render(request, 'appointments/calendar.html')