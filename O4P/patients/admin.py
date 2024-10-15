from django.contrib import admin
from .models import PatientInformation
from .models import PatientNotes
# Register your models here.

@admin.register(PatientInformation)
class PatientInformationAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'date_of_birth', 'contact_number', 'city', 'province', 'condition')
    search_fields = ('first_name', 'last_name', 'contact_number')
    list_filter = ('city', 'province', 'condition')
    ordering = ('last_name', 'first_name')