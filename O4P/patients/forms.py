from django import forms
from allauth.account.forms import LoginForm
from .models import PatientInformation
from .models import PatientNotes
from accounts.forms import BaseSignupForm, BaseInformationForm

class PatientInformationForm(BaseInformationForm):
    class Meta(BaseInformationForm.Meta):
        model = PatientInformation
        fields = BaseInformationForm.Meta.fields + [
            'diagnosis', 'mother_name', 'mother_number', 
            'father_name', 'father_number', 'referring_doctor', 
            'school', 'initial_evaluation'
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
            'initial_evaluation': forms.Textarea(attrs={
                'placeholder': 'Initial Evaluation Notes',
                'class': 'form-control',
                'rows': 3
            }),
        }


class PatientSignupForm(BaseSignupForm):
    diagnosis = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'Diagnosis',
            'class': 'form-control'
        }),
        required=True
    )
    mother_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': "Mother's Name",
            'class': 'form-control'
        }),
        required=True
    )
    mother_number = forms.CharField(
        max_length=13,
        widget=forms.TextInput(attrs={
            'placeholder': "Mother's Contact Number",
            'class': 'form-control'
        }),
        required=True
    )
    father_name = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': "Father's Name",
            'class': 'form-control'
        }),
        required=True
    )
    father_number = forms.CharField(
        max_length=13,
        widget=forms.TextInput(attrs={
            'placeholder': "Father's Contact Number",
            'class': 'form-control'
        }),
        required=True
    )
    referring_doctor = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'Referring Doctor',
            'class': 'form-control'
        }),
        required=True
    )
    school = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'placeholder': 'School (if applicable)',
            'class': 'form-control'
        }),
        required=False  # Optional
    )
    initial_evaluation = forms.CharField(
        max_length=100,
        widget=forms.Textarea(attrs={
            'placeholder': 'Initial Evaluation Notes',
            'class': 'form-control',
            'rows': 3
        }),
        required=True
    )

    def save(self, request):
        user = super().save(request, role="Guardian")  
        PatientInformation.objects.create(
            account_id=user,
            first_name=self.cleaned_data.get("first_name"),
            middle_name=self.cleaned_data.get("middle_name"),
            last_name=self.cleaned_data.get("last_name"),
            date_of_birth=self.cleaned_data.get("date_of_birth"),
            contact_number=self.cleaned_data.get("contact_number"),
            city=self.cleaned_data.get("city"),
            province=self.cleaned_data.get("province"),
            sex=self.cleaned_data.get("sex"),
            nationality=self.cleaned_data.get("nationality"),
            religion=self.cleaned_data.get("religion"),
            diagnosis=self.cleaned_data.get("diagnosis"),
            mother_name=self.cleaned_data.get("mother_name"),
            mother_number=self.cleaned_data.get("mother_number"),
            father_name=self.cleaned_data.get("father_name"),
            father_number=self.cleaned_data.get("father_number"),
            referring_doctor=self.cleaned_data.get("referring_doctor"),
            school=self.cleaned_data.get("school"),
            initial_evaluation=self.cleaned_data.get("initial_evaluation"),
        )
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