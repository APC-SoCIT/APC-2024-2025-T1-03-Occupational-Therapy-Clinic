from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class PatientInformation(models.Model):
    account_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="information")
    first_name = models.CharField(max_length=50) 
    last_name = models.CharField(max_length=50)  
    date_of_birth = models.DateField()             
    contact_number = models.CharField(max_length=15) 
    city = models.CharField(max_length=50)           
    province = models.CharField(max_length=50)                  
    condition = models.CharField(max_length=50)    
    
    class Meta:
        verbose_name = "Patient Information"
        verbose_name_plural = "Patients Information"
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.contact_number}"

class PatientNotes(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes') 
    title = models.CharField(max_length=100)  
    session_date = models.DateField()         
    content = models.TextField()               

    def __str__(self):
        return f"{self.title} - {self.patient.username} - {self.session_date}"