from django.contrib import admin
from .models import TherapistInformation, AssistantInformation, GuardianInformation
# Register your models here.

@admin.register(TherapistInformation)
class TherapistInformationAdmin(admin.ModelAdmin):
    list_display = ('id', 'account_id', 'first_name', 'last_name', 'account_id', 'specialization')
    search_fields = ('first_name', 'last_name', 'specialization')

@admin.register(AssistantInformation)
class AssistantInformationAdmin(admin.ModelAdmin):
    list_display = ('id', 'account_id', 'first_name', 'last_name', 'account_id', 'contact_number')
    search_fields = ('first_name', 'last_name')

@admin.register(GuardianInformation)
class GuardianInformationAdmin(admin.ModelAdmin):
    list_display = ('id', 'account_id', 'first_name', 'last_name', 'account_id')
    search_fields = ('first_name', 'last_name')