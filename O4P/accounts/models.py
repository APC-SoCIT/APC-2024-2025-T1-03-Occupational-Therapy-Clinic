from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class BaseInformation(models.Model):
    account_id = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50) 
    middle_name = models.CharField(max_length=50, blank=True, null=True) 
    last_name = models.CharField(max_length=50)  
    date_of_birth = models.DateField()             
    contact_number = models.CharField(
        max_length=13,  
        validators=[
            RegexValidator(
                regex=r'^(\+63|0)9\d{9}$',  
                message="Phone number must be entered in the format: '+639123456789' or '09123456789'."
            )
        ]
    )
    city = models.CharField(max_length=50)           
    province = models.CharField(max_length=50)                  

    class Meta:
        abstract = True
        verbose_name = "User Information"
        verbose_name_plural = "User Information"

        indexes = [
        models.Index(fields=['account_id']),
    ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.contact_number}"
    
class TherapistInformation(BaseInformation):
    specialization = models.CharField(max_length=100, blank=True, null=True)  

    class Meta:
        verbose_name = "Therapist Information"
        verbose_name_plural = "Therapist Information"

class AssistantInformation(BaseInformation):

    class Meta:
        verbose_name = "Assistant Information"
        verbose_name_plural = "Assistant Information"

class GuardianInformation(BaseInformation):
    relationship_to_patient = models.CharField(max_length=50, blank=True, null=True) 

    class Meta:
        verbose_name = "Guardian Information"
        verbose_name_plural = "Guardian Information"
