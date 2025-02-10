from django.contrib import admin
from .models import TherapistInformation, AssistantInformation, GuardianInformation, Province, Municipality
# Register your models here.

@admin.register(TherapistInformation)
class TherapistInformationAdmin(admin.ModelAdmin):
    list_display = ('id', 'account_id', 'first_name', 'last_name', 'account_id', 'specialization', 'province', 'municipality')
    search_fields = ('first_name', 'last_name', 'specialization')

@admin.register(AssistantInformation)
class AssistantInformationAdmin(admin.ModelAdmin):
    list_display = ('id', 'account_id', 'first_name', 'last_name', 'account_id', 'contact_number', 'province', 'municipality')
    search_fields = ('first_name', 'last_name')

@admin.register(GuardianInformation)
class GuardianInformationAdmin(admin.ModelAdmin):
    list_display = ('id', 'account_id', 'first_name', 'last_name', 'account_id', 'province', 'municipality')
    search_fields = ('first_name', 'last_name')

    
