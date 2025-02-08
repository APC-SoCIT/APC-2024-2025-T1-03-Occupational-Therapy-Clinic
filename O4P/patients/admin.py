from django.contrib import admin
from .models import PatientInformation
from .models import PatientNotes
from .models import Guardian
# Register your models here.

@admin.register(PatientInformation)
class PatientInformationAdmin(admin.ModelAdmin):
    list_display = ('id', 'account_id','first_name', 'last_name', 'date_of_birth', 'contact_number', 'city', 'province', 'relationship_to_guardian')
    search_fields = ('first_name', 'last_name', 'contact_number')
    list_filter = ('city', 'province',)
    ordering = ('last_name', 'first_name')

@admin.register(Guardian)
class GuardianAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)

@admin.register(PatientNotes)
class PatientNotesAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient_id', 'author', 'title', 'session_date', 'content')
    
    