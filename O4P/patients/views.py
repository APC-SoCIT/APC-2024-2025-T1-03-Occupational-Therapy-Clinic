from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.views.generic.edit import DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from .models import PatientInformation
from .models import PatientNotes
from .forms import PatientInformationForm
from core.mixins import UserRoleMixin
from django.core.exceptions import PermissionDenied

class PatientsListView(LoginRequiredMixin, ListView, UserRoleMixin):
    model = PatientInformation
    context_object_name = "patients"
    template_name = "patients/patients_list.html"
    login_url="/login"
    
    def get_queryset(self):
        return self.get_role_based_queryset(PatientInformation.objects.all(), PatientInformation)

class PatientDetailView(LoginRequiredMixin, DetailView,):
    model = PatientInformation
    template_name = 'patients/patients_detail.html'
    context_object_name = "patient"
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)  
        
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


class PatientsCreateView(LoginRequiredMixin,CreateView, UserRoleMixin):
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
        return self.request.user.groups.filter(name__in=['Therapist']).exists()
    
    def get_queryset(self):
        user = self.request.user
        
        if user.groups.filter(name='Patient').exists():
            raise PermissionDenied