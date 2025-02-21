from datetime import datetime
from django.views.generic import TemplateView, ListView, UpdateView, DetailView, DeleteView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from allauth.account.views import SignupView
from patients.models import PatientInformation, Guardian
from .forms import TherapistSignupForm, AssistantSignupForm, GuardianSignupForm, TherapistInformationForm, AssistantInformationForm, GuardianInformationForm
from allauth.account.views import SignupView
from core.mixins import RolePermissionRequiredMixin, CustomLoginRequiredMixin, UserRoleMixin
from .models import TherapistInformation, GuardianInformation, AssistantInformation, Province, Municipality
from django.http import Http404
from django.core.exceptions import PermissionDenied
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.http import JsonResponse
import requests
from accounts.forms import AssistantInformationForm, TherapistInformationForm



class WelcomeView(LoginRequiredMixin, UserRoleMixin, TemplateView):
    template_name = 'account/welcome.html'
    extra_context = {'today': datetime.today()}
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

# ACCOUNT MANAGEMENT
class GuardianListView(LoginRequiredMixin, RolePermissionRequiredMixin, UserRoleMixin, ListView):
    allowed_roles = ['Therapist', 'Assistant']
    model = GuardianInformation
    context_object_name = "guardians"
    template_name = "manage/information_list/guardian_list.html"

    def get_queryset(self):
        queryset = self.get_role_based_queryset(GuardianInformation)
        search_query = self.request.GET.get('q', '')

        if search_query:
            queryset = queryset.filter(
                first_name__icontains=search_query
            ) | queryset.filter(
                last_name__icontains=search_query
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context
    
class GuardianDetailView(LoginRequiredMixin, RolePermissionRequiredMixin, UserRoleMixin, DetailView,):
    allowed_roles = ['Therapist', 'Assistant', 'Guardian'] 
    model = GuardianInformation
    template_name = 'manage/information_detail/guardian_detail'
    context_object_name = "guardian"
    
    def get_queryset(self):
        return self.get_role_based_queryset(GuardianInformation)
    
class GuardianUpdateView(LoginRequiredMixin, RolePermissionRequiredMixin, UserRoleMixin, UpdateView):
    allowed_roles = ['Therapist']
    model = GuardianInformation
    form_class = GuardianInformationForm
    template_name = "manage/guardian_form.html"
    
    def get_queryset(self):
        return self.get_role_based_queryset(GuardianInformation)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['guardian'] = self.object 
        context['role'] = 'guardian' 
        context['object'] = self.object
        return context
    
    def get_success_url(self):
        return reverse_lazy('guardian_detail', kwargs={'pk': self.object.pk})

class GuardianDeleteView(LoginRequiredMixin, RolePermissionRequiredMixin, UserRoleMixin, DeleteView):
    allowed_roles = ['Therapist']
    model = GuardianInformation
    template_name = "manage/information_delete.html"
    success_url = reverse_lazy('guardian_list')
    
    def get_queryset(self):
        return self.get_role_based_queryset(GuardianInformation)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Retrieve the GuardianInformation object
        guardian_info = self.get_object()

        # Retrieve the associated Guardian model using account_id
        try:
            guardian = Guardian.objects.get(user=guardian_info.account_id)
        except Guardian.DoesNotExist:
            guardian = None

        # Add the Guardian instance to the context to be displayed in the template
        context['guardian'] = guardian  # This will allow us to access guardian details in the template
        context['patients'] = PatientInformation.objects.filter(guardian=guardian) if guardian else None

        context['guardian_info'] = guardian_info  # This is your GuardianInformation object
        context['role'] = 'guardian'
        context['object'] = guardian_info

        return context

class AssistantListView(LoginRequiredMixin, RolePermissionRequiredMixin, UserRoleMixin, ListView):
    allowed_roles = ['Therapist', 'Assistant']
    model = AssistantInformation
    context_object_name = "assistants"
    template_name = "manage/information_list/assistant_list.html"

    def get_queryset(self):
        queryset = self.get_role_based_queryset(AssistantInformation)
        search_query = self.request.GET.get('q', '')

        if search_query:
            queryset = queryset.filter(
                first_name__icontains=search_query
            ) | queryset.filter(
                last_name__icontains=search_query
            ) 
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context
    
class AssistantDetailView(CustomLoginRequiredMixin,RolePermissionRequiredMixin, UserRoleMixin, DetailView,):
    allowed_roles = ['Therapist', 'Assistant']
    model = AssistantInformation
    template_name = 'manage/information_detail/assistant_detail'
    context_object_name = "assistant"
    
    def get_queryset(self):
        return self.get_role_based_queryset(AssistantInformation)
    
class AssistantUpdateView(LoginRequiredMixin, RolePermissionRequiredMixin, UserRoleMixin, UpdateView):
    allowed_roles = ['Therapist']
    model = AssistantInformation
    form_class = AssistantInformationForm
    template_name = "manage/assistant_form.html"
    
    def get_queryset(self):
        return self.get_role_based_queryset(AssistantInformation)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assistant'] = self.object  
        context['object'] = self.object
        context['role'] = 'assistant' 
        return context
    
    def get_success_url(self):
        return reverse_lazy('assistant_detail', kwargs={'pk': self.object.pk})

class AssistantDeleteView(LoginRequiredMixin, RolePermissionRequiredMixin, UserRoleMixin, DeleteView):
    allowed_roles = ['Therapist']
    model = AssistantInformation
    template_name = "manage/information_delete.html"
    success_url = reverse_lazy('assistant_list')
    
    def get_queryset(self):
        return self.get_role_based_queryset(AssistantInformation)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['assistant'] = get_object_or_404(AssistantInformation, pk=self.object.pk)  
        context['role'] = 'assistant' 
        context['object'] = self.object
        return context
    
class TherapistListView(LoginRequiredMixin, RolePermissionRequiredMixin, UserRoleMixin, ListView):
    allowed_roles = ['Therapist', 'Assistant']

    model = AssistantInformation
    context_object_name = "therapists"
    template_name = "manage/information_list/therapist_list.html"

    def get_queryset(self):
        queryset = self.get_role_based_queryset(TherapistInformation)
        search_query = self.request.GET.get('q', '')

        if search_query:
            queryset = queryset.filter(
                first_name__icontains=search_query
            ) | queryset.filter(
                last_name__icontains=search_query
            ) | queryset.filter(
                specialization__icontains=search_query
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '')
        return context

class TherapistDetailView(LoginRequiredMixin, RolePermissionRequiredMixin, UserRoleMixin, DetailView,):
    allowed_roles = ['Therapist', 'Assistant']
    
    model = TherapistInformation
    template_name = 'manage/information_detail/therapist_detail'
    context_object_name = "therapist"
    
    def get_queryset(self):
        return self.get_role_based_queryset(TherapistInformation)

class TherapistUpdateView(LoginRequiredMixin, RolePermissionRequiredMixin, UserRoleMixin, UpdateView):
    allowed_roles = ['Therapist']
    model = TherapistInformation
    success_url = reverse_lazy('therapist_list')
    form_class = TherapistInformationForm
    template_name = "manage/therapist_form.html"
    
    def get_queryset(self):
        return self.get_role_based_queryset(TherapistInformation)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['therapist'] = self.object  
        context['object'] = self.object
        context['role'] = 'therapist' 
        return context

class TherapistDeleteView(LoginRequiredMixin, RolePermissionRequiredMixin, UserRoleMixin, DeleteView):
    allowed_roles = ['Therapist']
    model = TherapistInformation
    template_name = "manage/information_delete.html"
    success_url = reverse_lazy('therapist_list')
    
    def get_queryset(self):
        return self.get_role_based_queryset(TherapistInformation)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['therapist'] = get_object_or_404(TherapistInformation, pk=self.object.pk)  
        context['role'] = 'therapist' 
        context['object'] = self.object
        return context
    
# SIGN UP VIEWS
class TherapistSignupView(CustomLoginRequiredMixin, RolePermissionRequiredMixin, SignupView):
    allowed_roles = ['Administrator']

    form_class = TherapistSignupForm
    template_name = "account/therapist_signup.html"
    extra_context = {'role_name': 'Therapist'}

class AssistantSignupView(CustomLoginRequiredMixin, RolePermissionRequiredMixin, SignupView):
    allowed_roles = ['Administrator']

    form_class = AssistantSignupForm
    template_name = "account/assistant_signup.html"
    extra_context = {'role_name': 'Assistant'}

class GuardianSignupView(SignupView):

    form_class = GuardianSignupForm
    template_name = "account/guardian_signup.html"
    extra_context = {'role_name': 'Guardian'}
    
# STAFF INFORMATION CREATION VIEW
class AssistantInformationCreateView(RolePermissionRequiredMixin, CreateView):
    model = AssistantInformation
    form_class = AssistantInformationForm
    template_name = "manage/creation/assistant_create_form.html"
    allowed_roles = ['Assistant']
    success_url = reverse_lazy('welcome')

    def form_valid(self, form):
        form.instance.account_id = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class TherapistInformationCreateView(RolePermissionRequiredMixin, CreateView):
    model = TherapistInformation
    form_class = TherapistInformationForm
    template_name = "manage/creation/therapist_create_form.html"
    allowed_roles = ['Therapist']
    success_url = reverse_lazy('welcome')

    def form_valid(self, form):
        form.instance.account_id = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context
    
def get_municipalities(request):
    province_code = request.GET.get('province_code')
 
    if not province_code:
        return JsonResponse({'error': 'Province code required'}, status=400)

    municipalities = Municipality.objects.filter(province__code=province_code).order_by('name')
    municipalities_data = [{'code': m.code, 'name': m.name} for m in municipalities]

    return JsonResponse({'municipalities': municipalities_data})

