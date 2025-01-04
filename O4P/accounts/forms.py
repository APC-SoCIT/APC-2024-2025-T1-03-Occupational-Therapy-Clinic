from django import forms
from django.contrib.auth.models import Group
from allauth.account.forms import SignupForm
from patients.forms import CustomSignupForm
import datetime

class TherapistSignupForm(CustomSignupForm):
    def save(self, request):
        user = super().save(request)
        therapist_group = Group.objects.get(name='Therapist')
        user.groups.add(therapist_group)
        return user

class AssistantSignupForm(CustomSignupForm):
    def save(self, request):
        user = super().save(request)
        assistant_group = Group.objects.get(name='Assistant')
        user.groups.add(assistant_group)
        return user

class GuardianSignupForm(CustomSignupForm):
    def save(self, request):
        user = super().save(request)
        guardian_group = Group.objects.get(name='Guardian')
        user.groups.add(guardian_group)
        return user

