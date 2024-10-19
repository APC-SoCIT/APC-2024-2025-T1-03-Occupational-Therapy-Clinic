from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
# from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic import CreateView
from django.contrib.auth.forms import UserCreationForm

from patients.models import PatientInformation
class WelcomeView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/welcome.html'
    login_url = '/login'
    extra_context = {'today': datetime.today()}
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Add role flags to the context using the mixin logic
        context['is_patient'] = user.groups.filter(name='Patient').exists()
        context['is_guardian'] = user.groups.filter(name='Guardian').exists()
        context['is_therapist'] = user.groups.filter(name='Therapist').exists()
        context['is_assistant'] = user.groups.filter(name='Assistant').exists()
        context['is_administrator'] = user.is_superuser

        if context['is_patient']:
            # Assuming a patient has only one information record
            patient_info = PatientInformation.objects.filter(account_id=user).first()
            context['patient'] = patient_info

        return context
class LoginInterfaceView(LoginView):
    template_name='accounts/login.html'
    
class LogoutInterfaceView(LogoutView):
    template_name='accounts/logout.html'
    
class SignupView(CreateView):
    form_class = UserCreationForm
    template_name='accounts/register.html'
    success_url='accounts/login.html'
