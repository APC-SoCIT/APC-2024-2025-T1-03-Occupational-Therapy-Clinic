from django import forms
from .models import DAYS_OF_WEEK

SLOT_CHOICES = [
    ('08:00-09:00', '08:00-09:00'),
    ('09:00-10:00', '09:00-10:00'),
    ('10:00-11:00', '10:00-11:00'),
    ('11:00-12:00', '11:00-12:00'),
    ('13:00-14:00', '13:00-14:00'),
    ('14:00-15:00', '14:00-15:00'),
    ('15:00-16:00', '15:00-16:00'),
]

class TherapistScheduleForm(forms.Form):
    available_days = forms.MultipleChoiceField(
        choices=DAYS_OF_WEEK,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    available_slots = forms.MultipleChoiceField(
        choices=SLOT_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
