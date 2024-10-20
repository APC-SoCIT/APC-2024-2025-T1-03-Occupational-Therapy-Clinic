from django import forms
from django.contrib.auth.models import Group
from allauth.account.forms import SignupForm
from django.core.exceptions import ValidationError

import datetime
from .models import PatientInformation

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
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    date_of_birth = forms.DateField(
        widget=forms.SelectDateWidget(
            years=range(1940, datetime.date.today().year)  
        )
    )
    contact_number = forms.CharField(max_length=15)
    city = forms.CharField(max_length=50)
    province = forms.CharField(max_length=50)
    condition = forms.CharField(max_length=50)

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