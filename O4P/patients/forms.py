from django import forms
from allauth.account.forms import LoginForm
from .models import PatientInformation
from .models import PatientNotes
from accounts.forms import BaseSignupForm, BaseInformationForm

class PatientInformationForm(BaseInformationForm):
    class Meta(BaseInformationForm.Meta):
        model = PatientInformation
        fields = [
            field for field in BaseInformationForm.Meta.fields if field != "contact_number"
        ] + [
            "diagnosis", "mother_name", "mother_number", 
            "father_name", "father_number", "referring_doctor", 
            "school", "relationship_to_guardian", "initial_evaluation"
        ]
        labels = {
            **BaseInformationForm.Meta.labels,
            'diagnosis': 'Diagnosis',
            'mother_name': "Mother's Name",
            'mother_number': "Mother's Contact Number",
            'father_name': "Father's Name",
            'father_number': "Father's Contact Number",
            'referring_doctor': 'Referring Doctor',
            'school': 'School (if applicable)',
            'relationship_to_guardian': 'Relationship to guardian',
            'initial_evaluation': 'Initial Evaluation Notes',
        }
        widgets = {
            **BaseInformationForm.Meta.widgets,
            'diagnosis': forms.TextInput(attrs={
                'placeholder': 'Diagnosis',
                'class': 'form-control'
            }),
            'mother_name': forms.TextInput(attrs={
                'placeholder': "Mother's Name",
                'class': 'form-control'
            }),
            'mother_number': forms.TextInput(attrs={
                'placeholder': "Mother's Contact Number",
                'class': 'form-control'
            }),
            'father_name': forms.TextInput(attrs={
                'placeholder': "Father's Name",
                'class': 'form-control'
            }),
            'father_number': forms.TextInput(attrs={
                'placeholder': "Father's Contact Number",
                'class': 'form-control'
            }),
            'referring_doctor': forms.TextInput(attrs={
                'placeholder': 'Referring Doctor',
                'class': 'form-control'
            }),
            'school': forms.TextInput(attrs={
                'placeholder': 'School (if applicable)',
                'class': 'form-control'
            }),
            'school': forms.TextInput(attrs={
                'placeholder': 'School (if applicable)',
                'class': 'form-control'
            }),
            'initial_evaluation': forms.Textarea(attrs={
                'placeholder': 'Initial Evaluation Notes',
                'class': 'form-control',
                'rows': 3
            }),
        }

class CustomLoginForm(LoginForm):

    def login(self, *args, **kwargs):
        return super(CustomLoginForm, self).login(*args, **kwargs)

class PatientNotesForm(forms.ModelForm):
    class Meta:
        model = PatientNotes
        fields = ['title', 'session_date', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'style': 'width: 92%;',
                }),
            'session_date': forms.DateInput(attrs={
                'type': 'date',
                'style': 'width: 80%;',
                }),
            'content': forms.Textarea(attrs={
                'rows': 4,
                'style': 'width: 100%;',
                }),
        }