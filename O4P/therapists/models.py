from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import TherapistInformation  

User = get_user_model()

DAYS_OF_WEEK = [
    ('monday', 'Monday'),
    ('tuesday', 'Tuesday'),
    ('wednesday', 'Wednesday'),
    ('thursday', 'Thursday'),
    ('friday', 'Friday'),
    ('saturday', 'Saturday'),
    ('sunday', 'Sunday'),
]

class AvailableSlot(models.Model):
    # ✅ Use TherapistInformation from accounts instead of Therapist from therapists
    therapist = models.ForeignKey(TherapistInformation, on_delete=models.CASCADE, related_name='available_slots')
    day = models.CharField(max_length=10, choices=DAYS_OF_WEEK)
    start_time = models.TimeField()
    end_time = models.TimeField()

    class Meta:
        unique_together = ('therapist', 'day', 'start_time', 'end_time')
