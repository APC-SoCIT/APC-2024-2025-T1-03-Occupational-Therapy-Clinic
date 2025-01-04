from django.shortcuts import render
from django.http import HttpResponse
from datetime import datetime
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from allauth.account.views import SignupView
from django.http import HttpResponseForbidden
from patients.models import PatientInformation
from .forms import TherapistSignupForm, AssistantSignupForm, GuardianSignupForm
from allauth.account.views import SignupView
from core.mixins import RolePermissionRequiredMixin

class WelcomeView(LoginRequiredMixin, TemplateView):
    template_name = 'account/welcome.html'
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

class RoleBasedSignupView(SignupView):
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.groups.filter(name__in=['Administrator', 'Therapist']).exists():
            return HttpResponseForbidden("You do not have permission to access this page.")
        return super().dispatch(request, *args, **kwargs)

class TherapistSignupView(RolePermissionRequiredMixin, SignupView):
    allowed_roles = ['Administrator']

    form_class = TherapistSignupForm
    template_name = "account/signup.html"
    extra_context = {'role_name': 'Therapist'}

class AssistantSignupView(RolePermissionRequiredMixin, SignupView):
    allowed_roles = ['Therapist', 'Administrator']

    form_class = AssistantSignupForm
    template_name = "account/signup.html"
    extra_context = {'role_name': 'Assistant'}

class GuardianSignupView(RolePermissionRequiredMixin, SignupView):
    allowed_roles = ['Therapist', 'Administrator']

    form_class = GuardianSignupForm
    template_name = "account/signup.html"
    extra_context = {'role_name': 'Guardian'}