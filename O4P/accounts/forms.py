from django.contrib.auth.models import Group
from allauth.account.forms import SignupForm
from django import forms
from patients.models import PatientInformation
from patients.models import Guardian
from .models import TherapistInformation, AssistantInformation, GuardianInformation
import datetime
import re

class BaseSignupForm(SignupForm):
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'}),
        required=True
    )
    middle_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'}),
        required=True
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'}),
        required=True
    )
    date_of_birth = forms.DateField(
        widget=forms.SelectDateWidget(
            years=range(datetime.date.today().year - 100, datetime.date.today().year + 1),
        ),required=True
    )
    contact_number = forms.CharField(
        max_length=13,
        widget=forms.TextInput(attrs={'placeholder': '09123456789 / +639123456789'}),
        required=True
    )
    city = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'City'}),
        required=True
    )
    province = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Province'}),
        required=True
    )
    
    def clean(self):
        cleaned_data = super().clean()  
        date_of_birth = cleaned_data.get("date_of_birth")
        contact_number = cleaned_data.get("contact_number")

        if date_of_birth and date_of_birth > datetime.date.today():
            self.add_error("date_of_birth", "Invalid date of birth.")
        if contact_number and not re.match(r'^(\+63|0)9\d{9}$', contact_number):
            self.add_error("contact_number", "Invalid phone number format.")

        return cleaned_data
    def save(self, request, role=None):
        user = super().save(request)

        if not role:
            raise ValueError("No role defined for this form.")

        group = Group.objects.get(name=role)
        user.groups.add(group)
        
        base_information_data = {
            "account_id": user,
            "first_name": self.cleaned_data.get("first_name"),
            "middle_name": self.cleaned_data.get("middle_name"),
            "last_name": self.cleaned_data.get("last_name"),
            "date_of_birth": self.cleaned_data.get("date_of_birth"),
            "contact_number": self.cleaned_data.get("contact_number"),
            "city": self.cleaned_data.get("city"),
            "province": self.cleaned_data.get("province")
        }

        if role == "Therapist":           
            TherapistInformation.objects.create(
                **base_information_data,
                specialization=self.cleaned_data.get("specialization") 
            )
        elif role == "Assistant":
            AssistantInformation.objects.create(
                **base_information_data
            )
        elif role == "Guardian":
            GuardianInformation.objects.create(
                **base_information_data,
                relationship_to_patient=""  
            )
        elif role == "Patient":
            PatientInformation.objects.create(
                **base_information_data,
                condition=self.cleaned_data['condition'],
            )
        else:
            raise ValueError(f"Unsupported role: {role}")
        return user

class TherapistSignupForm(BaseSignupForm):
    specialty = forms.CharField(
                    max_length=50,
                    widget=forms.TextInput(attrs={'placeholder': 'Specialty'}),
                    required=True
                                )
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
    relationship_to_patient = forms.CharField(
                    max_length=50,
                    widget=forms.TextInput(attrs={'placeholder': 'Relationship'}), 
                    required=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['assigned_patients'].queryset = PatientInformation.objects.filter(
            guardian__isnull=True  
        )

        self.fields['assigned_patients'].label_from_instance = lambda obj: (
            f"{obj.first_name} {obj.last_name} ({obj.account_id.email})"
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

# INFORMATION FORMS

class TherapistInformationForm(forms.ModelForm):
    class Meta:
        model = TherapistInformation
        fields = [
            'first_name', 'last_name', 'date_of_birth', 
            'contact_number', 'city', 'province', 
            'specialization'
        ]
        widgets = {
            'date_of_birth': forms.SelectDateWidget(years=range(datetime.date.today().year - 100, datetime.date.today().year + 1)),
        }

class AssistantInformationForm(forms.ModelForm):
    class Meta:
        model = AssistantInformation
        fields = [
            'first_name', 'last_name', 'date_of_birth', 
            'contact_number', 'city', 'province'
        ]
        widgets = {
            'date_of_birth': forms.SelectDateWidget(years=range(datetime.date.today().year - 100, datetime.date.today().year + 1)),
        }

class GuardianInformationForm(forms.ModelForm):
    class Meta:
        model = GuardianInformation
        fields = [
            'first_name', 'last_name', 'date_of_birth', 
            'contact_number', 'city', 'province', 
            'relationship_to_patient'
        ]
        widgets = {
            'date_of_birth': forms.SelectDateWidget(years=range(datetime.date.today().year - 100, datetime.date.today().year + 1)),
        }