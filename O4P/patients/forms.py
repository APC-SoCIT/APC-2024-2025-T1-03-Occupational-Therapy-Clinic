from django import forms
from allauth.account.forms import LoginForm
from .models import PatientInformation
from .models import PatientNotes
from accounts.forms import BaseSignupForm

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

class PatientSignupForm(BaseSignupForm):
    condition = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Medical Condition'})
    )

    def save(self, request):
        user = super().save(request, role="Patient") 
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