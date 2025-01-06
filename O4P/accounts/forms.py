from django.contrib.auth.models import Group
from allauth.account.forms import SignupForm
from django import forms
from patients.models import PatientInformation
from patients.models import Guardian

class BaseSignupForm(SignupForm):
    def save(self, request, role=None):
        user = super().save(request)

        if not role:
            raise ValueError("No role defined for this form. Please set 'role' in the subclass.")

        group = Group.objects.get(name=role)
        user.groups.add(group)
        return user

class TherapistSignupForm(BaseSignupForm):
    def save(self, request):
        user = super().save(request, role="Therapist") 
        return user

class AssistantSignupForm(BaseSignupForm):
    def save(self, request):
        user = super().save(request, role="Assistant") 
        return user

class GuardianSignupForm(BaseSignupForm):
    assigned_patients = forms.ModelMultipleChoiceField(
        queryset=PatientInformation.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Assigned Patient/s",
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['assigned_patients'].queryset = PatientInformation.objects.filter(guardian__isnull=True)

        self.fields['assigned_patients'].label_from_instance = lambda obj: (
            f"{obj.first_name} {obj.last_name}"
        )
    
    def save(self, request):
        user = super().save(request, role="Guardian")
        
        guardian = Guardian.objects.create(user=user)
        
        assigned_patients = self.cleaned_data.get('assigned_patients')
        if assigned_patients:
            for patient_info in assigned_patients:
                patient_info.guardian = guardian 
                patient_info.save() 
                
        return user



