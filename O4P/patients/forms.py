from django import forms
from allauth.account.forms import LoginForm
from .models import PatientInformation
from .models import PatientNotes
from accounts.forms import BaseSignupForm, BaseInformationForm

class PatientInformationForm(BaseInformationForm):
    class Meta(BaseInformationForm.Meta):
        model = PatientInformation
        fields = BaseInformationForm.Meta.fields + ['condition', 'guardian']
        labels = {
            **BaseInformationForm.Meta.labels,
            'condition': 'Medical Condition',
            'guardian': 'Guardian',
        }
        widgets = {
            **BaseInformationForm.Meta.widgets,
            'condition': forms.TextInput(attrs={'class': 'form-control'}),
            'guardian': forms.Select(attrs={'class': 'form-control'}),
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