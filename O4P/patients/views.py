from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.generic.edit import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import PatientInformation
from .models import PatientNotes
from .forms import PatientInformationForm
from .models import Guardian
from core.mixins import UserRoleMixin
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.shortcuts import redirect

from allauth.account.views import SignupView

class PatientsListView(LoginRequiredMixin, UserRoleMixin, ListView):
    model = PatientInformation
    context_object_name = "patients"
    template_name = "patients/patients_list.html"

    def get_queryset(self):
        user = self.request.user
        
        if user.groups.filter(name='Patient').exists():
            raise PermissionDenied
        
        return self.get_role_based_queryset(PatientInformation)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class PatientDetailView(LoginRequiredMixin, UserRoleMixin, DetailView,):
    model = PatientInformation
    template_name = 'patients/patients_detail.html'
    context_object_name = "patient"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        patient = self.get_object()

        context['patient_notes'] = PatientNotes.objects.filter(patient_id=patient)

        user = self.request.user
        context['is_patient'] = user.groups.filter(name='Patient').exists()
        context['is_guardian'] = user.groups.filter(name='Guardian').exists()
        context['is_assistant'] = user.groups.filter(name='Assistant').exists()
        context['is_therapist'] = user.groups.filter(name='Therapist').exists()
        context['is_administrator'] = user.is_superuser

        return context
    
    def get_queryset(self):
        return self.get_role_based_queryset(PatientInformation)
    
class PatientsUpdateView(LoginRequiredMixin, UserRoleMixin, UpdateView):
    model = PatientInformation
    success_url = '/patients'
    form_class = PatientInformationForm
    template_name = "patients/patients_form.html"
   
    def test_func(self):
        return self.request.user.groups.filter(name__in=['Therapist', 'Administrator']).exists()
    
    def get_queryset(self):
        user = self.request.user
        
        if user.groups.filter(name__in=['Patient', 'Guardian', 'Assistant']).exists():
            raise PermissionDenied
       
        return super().get_queryset()

class PatientsDeleteView(LoginRequiredMixin, UserRoleMixin, DeleteView):
    model = PatientInformation
    template_name = "patients/patients_delete.html"
    success_url = '/patients'
    
    def test_func(self):
        return self.request.user.groups.filter(name__in=['Therapist', 'Administrator']).exists()
    
    def get_queryset(self):
        user = self.request.user
        
        if user.groups.filter(name__in=['Patient', 'Guardian', 'Assistant']).exists():
            raise PermissionDenied
        
        return super().get_queryset()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['patient'] = get_object_or_404(PatientInformation, pk=self.object.pk)  # Ensure patient is in context
        return context

class NoteDetailView(LoginRequiredMixin, DetailView):
    model = PatientNotes
    template_name = 'patients_notes/note_details.html'
    context_object_name = "note"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        note = self.get_object()

        context['patient_notes'] = PatientNotes.objects.filter(patient=note.patient)

        user = self.request.user
        context['is_patient'] = user.groups.filter(name='Patient').exists()
        context['is_guardian'] = user.groups.filter(name='Guardian').exists()
        context['is_assistant'] = user.groups.filter(name='Assistant').exists()
        context['is_therapist'] = user.groups.filter(name='Therapist').exists()
        context['is_administrator'] = user.is_superuser

        return context
    
    def get_queryset(self):
        user = self.request.user
        
        if user.groups.filter(name='Patient').exists():
            return PatientNotes.objects.filter(patient__account_id=user)
        elif user.groups.filter(name='Guardian').exists():
            try:
                guardian = Guardian.objects.get(user=user)  
                return PatientNotes.objects.filter(patient__guardian=guardian)  
            except Guardian.DoesNotExist:
                return PatientNotes.objects.none() 
        elif user.groups.filter(name__in=['Therapist', 'Assistant', 'Administrator']).exists():
            return PatientNotes.objects.all()
        else:
            raise PermissionDenied