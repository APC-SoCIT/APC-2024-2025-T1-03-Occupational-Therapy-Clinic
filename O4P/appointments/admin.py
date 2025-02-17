from django.contrib import admin
from .models import Appointment
from .models import AppointmentRequest

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("id", "therapist", "patient", "date", "start_time", "status")
    list_filter = ("status", "date", "therapist")
    search_fields = ("patient__first_name", "patient__last_name", "therapist__first_name", "therapist__last_name")
    ordering = ("-date", "start_time")  # Show latest appointments first

@admin.register(AppointmentRequest)
class AppointmentRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "therapist", "requested_date", "requested_time", "status")
    list_filter = ("status", "requested_date", "therapist")
    search_fields = ("first_name", "last_name", "therapist__first_name", "therapist__last_name")
    ordering = ("-requested_date", "requested_time")