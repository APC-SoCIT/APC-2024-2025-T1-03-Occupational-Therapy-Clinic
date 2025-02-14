from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from datetime import date
from .nationalities import NATIONALITIES_duble_tuple_for as Nationalities

#GEOGRAPHY MODELS FOR FORMS
class Province(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Municipality(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    province = models.ForeignKey(Province, on_delete=models.CASCADE, related_name="municipalities")

    def __str__(self):
        return self.name
    
class BaseInformation(models.Model):
    account_id = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50) 
    middle_name = models.CharField(max_length=50, blank=True, null=True) 
    last_name = models.CharField(max_length=50)  
    date_of_birth = models.DateField()  

    @property
    def age(self):
        today = date.today()
        age = today.year - self.date_of_birth.year
        if (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day):
            age -= 1
        return age  
             
    contact_number = models.CharField(
        max_length=13,  
        validators=[
            RegexValidator(
                regex=r'^(\+63|0)9\d{9}$',  
                message="Phone number must be entered in the format: '+639123456789' or '09123456789'."
            )
        ]
    )
    
    sex_choices = (
        ('M', 'Male'),
        ('F', 'Female')
    )
    sex = models.CharField(max_length=1, choices=sex_choices, blank=True, null=True)    
    province = models.ForeignKey(Province, on_delete=models.SET_NULL, null=True, blank=True, related_name="%(class)s_residents")
    municipality = models.ForeignKey(Municipality, on_delete=models.SET_NULL, null=True, blank=True, related_name="%(class)s_residents")
    nationality = models.CharField(
        max_length=30,
        choices=Nationalities, 
        blank=True,
        null=True
    )              

    class Meta:
        abstract = True
        verbose_name = "User Information"
        verbose_name_plural = "User Information"

        indexes = [
        models.Index(fields=['account_id']),
    ]
    
    def __str__(self):
        return f"{self.first_name} {self.middle_name} - {self.last_name} - {self.contact_number}"
    
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

    class Meta:
        verbose_name = "Guardian Information"
        verbose_name_plural = "Guardian Information"


