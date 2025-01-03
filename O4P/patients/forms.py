from django import forms
from django.contrib.auth.models import Group
from allauth.account.forms import SignupForm
from allauth.account.forms import LoginForm
from django.core.exceptions import ValidationError

import datetime
from .models import PatientInformation
from .models import PatientNotes

class PatientInformationForm(forms.ModelForm):
    class Meta:
        model = PatientInformation
        fields = [
            'first_name', 'last_name', 'date_of_birth', 
            'contact_number', 'city', 'province', 'condition'
        ]
        labels = {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'date_of_birth': 'Date of Birth',
            'contact_number': 'Contact Number',
            'city': 'City',
            'province': 'Province',
            'condition': 'Medical Condition'
        }
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'contact_number': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'province': forms.TextInput(attrs={'class': 'form-control'}),
            'condition': forms.TextInput(attrs={'class': 'form-control'}),
        }

class CustomSignupForm(SignupForm):
    first_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Last Name'})
    )
    date_of_birth = forms.DateField(
        widget=forms.SelectDateWidget(
            years=range(1940, datetime.date.today().year)
        )
    )
    contact_number = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'placeholder': 'Contact Number'})
    )
    city = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'City'})
    )
    province = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Province'})
    )
    condition = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Medical Condition'})
    )
    

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)

        PatientInformation.objects.create(
            account_id=user,
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            date_of_birth=self.cleaned_data['date_of_birth'],
            contact_number=self.cleaned_data['contact_number'],
            city=self.cleaned_data['city'],
            province=self.cleaned_data['province'],
            condition=self.cleaned_data['condition'],
        )

        user.groups.add(Group.objects.get(name='Patient'))

        return user

class CustomLoginForm(LoginForm):

    def login(self, *args, **kwargs):
        return super(CustomLoginForm, self).login(*args, **kwargs)
    
class PatientNotesForm(forms.ModelForm):
    class Meta:
        model = PatientNotes
        fields = ['title', 'session_date', 'content']
        widgets = {
            'session_date': forms.DateInput(attrs={'type': 'date'}),
            'content': forms.Textarea(attrs={'rows': 4}),
        }