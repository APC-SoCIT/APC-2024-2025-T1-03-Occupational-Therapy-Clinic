from datetime import datetime
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from allauth.account.views import SignupView
from patients.models import PatientInformation
from patients.forms import PatientSignupForm
from .forms import TherapistSignupForm, AssistantSignupForm, GuardianSignupForm
from allauth.account.views import SignupView
from core.mixins import RolePermissionRequiredMixin
from core.mixins import CustomLoginRequiredMixin

class WelcomeView(LoginRequiredMixin, TemplateView):
    template_name = 'account/welcome.html'
    extra_context = {'today': datetime.today()}
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        context['is_patient'] = user.groups.filter(name='Patient').exists()
        context['is_guardian'] = user.groups.filter(name='Guardian').exists()
        context['is_therapist'] = user.groups.filter(name='Therapist').exists()
        context['is_assistant'] = user.groups.filter(name='Assistant').exists()
        context['is_administrator'] = user.groups.filter(name='Administrator').exists()

        if context['is_patient']:
            patient_info = PatientInformation.objects.filter(account_id=user).first()
            context['patient'] = patient_info

        return context

class PatientSignupView(CustomLoginRequiredMixin, RolePermissionRequiredMixin, SignupView):
    allowed_roles = ['Administrator', 'Therapist']

    form_class = PatientSignupForm
    template_name = "account/signup.html"
    extra_context = {'role_name': 'Patient'}

class TherapistSignupView(CustomLoginRequiredMixin, RolePermissionRequiredMixin, SignupView):
    allowed_roles = ['Administrator']

    form_class = TherapistSignupForm
    template_name = "account/signup.html"
    extra_context = {'role_name': 'Therapist'}

class AssistantSignupView(CustomLoginRequiredMixin, RolePermissionRequiredMixin, SignupView):
    allowed_roles = ['Therapist', 'Administrator']

    form_class = AssistantSignupForm
    template_name = "account/signup.html"
    extra_context = {'role_name': 'Assistant'}

class GuardianSignupView(CustomLoginRequiredMixin, RolePermissionRequiredMixin, SignupView):
    allowed_roles = ['Therapist', 'Administrator']

    form_class = GuardianSignupForm
    template_name = "account/signup.html"
    extra_context = {'role_name': 'Guardian'}