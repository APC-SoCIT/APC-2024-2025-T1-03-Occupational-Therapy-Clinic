from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.generic.edit import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from .models import PatientInformation
from .models import PatientNotes
from .forms import PatientInformationForm
from core.mixins import UserRoleMixin
from django.core.exceptions import PermissionDenied

class PatientsListView(LoginRequiredMixin, UserRoleMixin, ListView ):
    model = PatientInformation
    context_object_name = "patients"
    template_name = "patients/patients_list.html"
    login_url="/login"
    
    def get_queryset(self):
        user = self.request.user

        if user.groups.filter(name='Patient').exists():
            raise PermissionDenied
        
        return self.get_role_based_queryset(PatientInformation)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        return context
        
class PatientDetailView(LoginRequiredMixin, DetailView,):
    model = PatientInformation
    template_name = 'patients/patients_details.html'
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

        return context
    
    def get_queryset(self):
        user = self.request.user

        if user.groups.filter(name__in=['Therapist', 'Assistant']).exists():
            return PatientInformation.objects.all()
        if user.groups.filter(name='Patient').exists():
            return PatientInformation.objects.filter(account_id=user)
        
        raise PermissionDenied

class PatientsCreateView(LoginRequiredMixin, UserRoleMixin, CreateView):
    model = PatientInformation
    success_url = '/patients'
    form_class = PatientInformation
    
    def test_func(self):
        return self.request.user.groups.filter(name__in=['Therapist']).exists()
    
    def get_queryset(self):
        user = self.request.user
        
        if user.groups.filter(name='Patient').exists():
            raise PermissionDenied
    
class PatientsUpdateView(LoginRequiredMixin, UserRoleMixin, UserPassesTestMixin, UpdateView):
    model = PatientInformation
    template_name = "patients/patients_form.html"
    success_url = '/patients'
    form_class = PatientInformationForm
    
    def test_func(self):
        return self.request.user.groups.filter(name='Therapist').exists()

    def get_queryset(self):
        user = self.request.user
        
        if user and user.groups.filter(name='Patient').exists():
            raise PermissionDenied
        
        return super().get_queryset()

class PatientsDeleteView(LoginRequiredMixin, UserRoleMixin, DeleteView):
    model = PatientInformation
    template_name = "patients/patients_delete.html"
    success_url = '/patients'
    
    def test_func(self):
        return self.request.user.groups.filter(name='Therapist').exists()

    def get_queryset(self):
        user = self.request.user
        
        if user and user.groups.filter(name='Patient').exists():
            raise PermissionDenied
        
        return super().get_queryset()
       
# Patient Notes

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

        return context
    
    def get_queryset(self):
        user = self.request.user
        
        if user.groups.filter(name='Patient').exists():
            return PatientNotes.objects.filter(patient__account_id=user)
        #elif user.groups.filter(name='Guardian').exists():
        #    return PatientNotes.objects.filter(patient__guardian=user)  # Adjust this based on your model
        elif user.groups.filter(name__in=['Therapist', 'Assistant']).exists():
            return PatientNotes.objects.all()
        else:
            raise PermissionDenied