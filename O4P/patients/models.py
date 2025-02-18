from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from accounts.models import BaseInformation
from django.core.validators import RegexValidator
# Create your models here.
    
class PatientInformation(BaseInformation):              
    diagnosis = models.CharField(max_length=50)    
    mother_name = models.CharField(max_length=50)
    mother_number = models.CharField(
        max_length=13,  
        validators=[
            RegexValidator(
                regex=r'^(\+63|0)9\d{9}$',  
                message="Phone number must be entered in the format: '+639123456789' or '09123456789'."
            )
        ]
    )
    father_name = models.CharField(max_length=50)
    father_number = models.CharField(
        max_length=13,  
        validators=[
            RegexValidator(
                regex=r'^(\+63|0)9\d{9}$',  
                message="Phone number must be entered in the format: '+639123456789' or '09123456789'."
            )
        ]
    )
    referring_doctor = models.CharField(max_length=50)
    school = models.CharField(max_length=50, blank=True, null=True)
    initial_evaluation = models.CharField(max_length=100)
    relationship_to_guardian = models.CharField(max_length=50)
    contact_number = None
    religion = models.CharField(max_length=50, null=True) 
    
    class Meta:
        verbose_name = "Patient Information"
        verbose_name_plural = "Patient Information"
    
    def __str__(self):
        return f"{self.first_name} {self.middle_name} - {self.last_name} - {self.contact_number}"

class PatientNotes(models.Model):
    patient = models.ForeignKey(PatientInformation, on_delete=models.CASCADE, related_name="notes")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    title = models.CharField(max_length=100)  
    session_date = models.DateField()         
    content = models.TextField()               

    class Meta:
        verbose_name = "Patient Notes"
        verbose_name_plural = "Patient Notes"
        
    def __str__(self):
        return f"{self.title} - {self.patient.id} - {self.session_date}"
    
