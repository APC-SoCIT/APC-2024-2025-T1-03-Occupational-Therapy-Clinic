from django.contrib.auth.models import Group
from allauth.account.forms import SignupForm
from django import forms
from patients.models import PatientInformation
from patients.models import Guardian
from .models import TherapistInformation, AssistantInformation, GuardianInformation
import datetime, re, requests


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
    province = forms.ChoiceField(choices=[])
    city = forms.ChoiceField(choices=[])
    
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Fetch provinces
        response_provinces = requests.get('https://psgc.gitlab.io/api/provinces')
        if response_provinces.status_code == 200:
            provinces = response_provinces.json()
            sorted_provinces = sorted(provinces, key=lambda x: x['name'])
            self.fields['province'].choices = [
                (province['code'], province['name']) for province in sorted_provinces
            ]
        else:
            self.fields['province'].choices = []

        # Fetch cities
        response_cities = requests.get('https://psgc.gitlab.io/api/cities-municipalities')
        if response_cities.status_code == 200:
            cities = response_cities.json()
            sorted_cities = sorted(cities, key=lambda x: x['name'])
            self.fields['city'] = forms.ChoiceField(
                choices=[(city['code'], city['name']) for city in sorted_cities]
            )
        else:
            self.fields['city'] = forms.ChoiceField(choices=[])
            
    def clean(self):
        cleaned_data = super().clean()  
        date_of_birth = cleaned_data.get("date_of_birth")
        contact_number = cleaned_data.get("contact_number")

        if date_of_birth and date_of_birth > datetime.date.today():
            self.add_error("date_of_birth", "Invalid date of birth.")
        if contact_number and not re.match(r'^(\+63|0)9\d{9}$', contact_number):
            self.add_error("contact_number", "Invalid phone number format.")
            
        # Fetch the name of the province and city by their code
        province_code = cleaned_data.get('province')
        city_code = cleaned_data.get('city')
        
        response_provinces = requests.get('https://psgc.gitlab.io/api/provinces')
        if response_provinces.status_code == 200:
            provinces = response_provinces.json()
            province_name = next((province['name'] for province in provinces if province['code'] == province_code), None)
            cleaned_data['province'] = province_name

        response_cities = requests.get('https://psgc.gitlab.io/api/cities-municipalities')
        if response_cities.status_code == 200:
            cities = response_cities.json()
            city_name = next((city['name'] for city in cities if city['code'] == city_code), None)
            cleaned_data['city'] = city_name

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
            specialization = self.cleaned_data.get("specialization")
            
            TherapistInformation.objects.create(
                **base_information_data,
                specialization=specialization 
            )
        elif role == "Assistant":
            AssistantInformation.objects.create(
                **base_information_data
            )
        elif role == "Guardian":
            relationship_to_patient = self.cleaned_data.get("relationship_to_patient")
            GuardianInformation.objects.create(
                **base_information_data,
                relationship_to_patient=relationship_to_patient  
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
    specialization = forms.CharField(
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
            f"{obj.id}{obj.first_name} {obj.last_name} {obj.account_id.email}"
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

class BaseInformationForm(forms.ModelForm):
    class Meta:
        fields = [
            'first_name', 'middle_name', 'last_name', 'date_of_birth', 
            'contact_number', 'province', 'city'
        ]
        labels = {
            'first_name': 'First Name',
            'middle_name': 'Middle Name',
            'last_name': 'Last Name',
            'date_of_birth': 'Date of Birth',
            'contact_number': 'Contact Number',
            'province': 'Province',
            'city': 'City',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'province': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control', }),
        }
        


        
class TherapistInformationForm(BaseInformationForm):
    class Meta(BaseInformationForm.Meta):
        model = TherapistInformation
        fields = BaseInformationForm.Meta.fields + ['specialization']
        labels = {
            **BaseInformationForm.Meta.labels,
            'specialization': 'Specialization',
        }
        widgets = {
            **BaseInformationForm.Meta.widgets,
            'specialization': forms.TextInput(attrs={'class': 'form-control'}),
        }


class AssistantInformationForm(BaseInformationForm):
    class Meta(BaseInformationForm.Meta):
        model = AssistantInformation
        # No extra fields; inherits everything from BaseInformationForm


class GuardianInformationForm(BaseInformationForm):
    class Meta(BaseInformationForm.Meta):
        model = GuardianInformation
        fields = BaseInformationForm.Meta.fields + ['relationship_to_patient']
        labels = {
            **BaseInformationForm.Meta.labels,
            'relationship_to_patient': 'Relationship to Patient',
        }
        widgets = {
            **BaseInformationForm.Meta.widgets,
            'relationship_to_patient': forms.TextInput(attrs={'class': 'form-control'}),
        }