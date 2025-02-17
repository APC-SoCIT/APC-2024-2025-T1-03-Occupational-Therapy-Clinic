from django.contrib.auth.models import Group
from allauth.account.forms import SignupForm
from django import forms
from patients.models import PatientInformation
from patients.models import Guardian
from .models import TherapistInformation, AssistantInformation, GuardianInformation, Province, Municipality
import datetime, re, requests
from .nationalities import NATIONALITIES_duble_tuple_for as NATIONALITIES

class BaseSignupForm(SignupForm):
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )
    middle_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=True,
    )
    contact_number = forms.CharField(
        max_length=13,
        widget=forms.TextInput(attrs={'placeholder': '09123456789 / +639123456789', 'class': 'form-control'}),
        required=True
    )
    province = forms.ModelChoiceField(
        queryset=Province.objects.all().order_by('name'),
        empty_label="Select Province",
        to_field_name="code",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    municipality = forms.ModelChoiceField(
        queryset=Municipality.objects.none(),  
        empty_label="Select Municipality",
        to_field_name="code",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    sex = forms.ChoiceField(
        choices=(('M', 'Male'), ('F', 'Female')),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    nationality = forms.ChoiceField(
        choices=NATIONALITIES,
        required=True,
        initial='Filipino',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['municipality'].queryset = Municipality.objects.none()

        if 'province' in self.data:
            province_code = self.data.get('province')  
            if province_code:
                self.fields['municipality'].queryset = Municipality.objects.filter(province__code=province_code).order_by('name') 
            
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
            "province": self.cleaned_data.get("province"),
            "municipality": self.cleaned_data.get("municipality"),
            "sex": self.cleaned_data.get("sex"),
            "nationality": self.cleaned_data.get("nationality"),
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
            GuardianInformation.objects.create(
                **base_information_data,
            )
        else:
            raise ValueError(f"Unsupported role: {role}")
        return user

class TherapistSignupForm(BaseSignupForm):
    specialization = forms.CharField(
                    max_length=50,
                    widget=forms.TextInput(attrs={'placeholder': 'Specialty', 'class': 'form-control'}),
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
    def save(self, request):
        user = super().save(request, role="Guardian")
                
        return user

# INFORMATION FORMS

class BaseInformationForm(forms.ModelForm):
    class Meta:
        fields = [
            'first_name', 'middle_name', 'last_name', 'date_of_birth', 'sex', 'nationality', 
            'contact_number', 'province', 'municipality'
        ]
        labels = {
            'first_name': 'First Name',
            'middle_name': 'Middle Name',
            'last_name': 'Last Name',
            'date_of_birth': 'Date of Birth',
            'sex': 'Sex',
            'nationality': 'Nationality',
            'contact_number': 'Contact Number',
            'province': 'Province',
            'municipality': 'Municipality',
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'middle_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'sex': forms.Select(attrs={'class': 'form-control'}),
            'nationality': forms.Select(attrs={'class': 'form-control'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'province': forms.Select(attrs={'class': 'form-control'}),
            'municipality': forms.Select(attrs={'class': 'form-control'}),
        }
                
    province = forms.ModelChoiceField(
        queryset=Province.objects.all().order_by('name'),
        empty_label="Select Province",
        to_field_name="code",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    municipality = forms.ModelChoiceField(
        queryset=Municipality.objects.none(),  
        empty_label="Select Municipality",
        to_field_name="code",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )
    nationality = forms.ChoiceField(
        choices=NATIONALITIES,
        required=True,
        initial='Filipino',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If editing an existing instance, set municipality queryset
        if self.instance and self.instance.pk and self.instance.province:
            self.fields['municipality'].queryset = Municipality.objects.filter(province=self.instance.province).order_by('name')

        # If it's a new form submission, dynamically update queryset
        elif 'province' in self.data:
            try:
                province_id = self.data.get('province')
                self.fields['municipality'].queryset = Municipality.objects.filter(province__code=province_id).order_by('name')
            except ValueError:
                self.fields['municipality'].queryset = Municipality.objects.none()

    def clean_municipality(self):
        """Ensure selected municipality is valid within the province."""
        municipality = self.cleaned_data.get('municipality')
        province = self.cleaned_data.get('province')

        if municipality and province:
            # Check if the municipality belongs to the selected province
            if not Municipality.objects.filter(code=municipality.code, province=province).exists():
                raise forms.ValidationError("Invalid municipality selected for the given province.")

        return municipality
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
 