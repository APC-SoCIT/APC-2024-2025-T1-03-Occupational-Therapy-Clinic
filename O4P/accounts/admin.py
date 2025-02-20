from django.shortcuts import render
from django.urls import path
from django.contrib import admin
from django.db import models
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.utils import timezone
from django.utils.timezone import now
from collections import Counter
from django.db.models import Count  
from datetime import date, timedelta, datetime
from admincharts.admin import AdminChartMixin
from admincharts.utils import months_between_dates
from .models import TherapistInformation, AssistantInformation, GuardianInformation, Province, Municipality
from patients.models import PatientInformation, PatientNotes
from games.models import Game, AssignedGame
from appointments.models import Appointment, AppointmentRequest
from allauth.account.models import EmailAddress

# Register your models here.

# Unregister default User and Group admin
admin.site.unregister(User)
admin.site.unregister(Group)

# Create a new admin class with charts
class CustomUserAdmin(AdminChartMixin, UserAdmin):
    def get_list_chart_data(self, queryset):
        if not queryset:
            return {}

        earliest = queryset.order_by("date_joined").first().date_joined
        labels = []
        totals = []

        for b in months_between_dates(earliest, now()):
            labels.append(b.strftime("%b %Y"))
            totals.append(
                queryset.filter(date_joined__year=b.year, date_joined__month=b.month).count()
            )

        return {
            "labels": labels,
            "datasets": [{"label": "New Users", "data": totals, "backgroundColor": "#79aec8"}],
        }

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

class CustomAdminSite(admin.AdminSite):
    """Custom Admin Site with a dashboard view."""

    def generate_staff_chart(self):
        """Generate pie chart data for users grouped by their assigned group."""
        groups = Group.objects.exclude(name="Guardian")
        labels = []
        data = []

        for group in groups:
            user_count = group.user_set.count()  # Count users in each group
            if user_count > 0:
                labels.append(group.name)
                data.append(user_count)

        total_users = sum(data)

        return {
            "labels": labels,
            "datasets": [{
                "label": "Users by Group",
                "data": data,
                "backgroundColor": ["#36A2EB", "#4CAF50", "#004C99", "#2E7D32", "#85C1E9", "#66BB6A"],
                "borderColor": ["#004C99", "#2E7D32", "#002855", "#1B5E20", "#00509E", "#388E3C"],
                "borderWidth": 2,
                "hoverBackgroundColor": ["#85C1E9", "#66BB6A", "#5C87B3", "#81C784", "#99CCFF", "#A5D6A7"],
                "hoverBorderColor": "#000000"
            }],
            "options": {
                "plugins": {
                    "tooltip": {
                        "callbacks": {
                            "label": "function(context) { let value = context.raw; let total = " + str(total_users) + "; let percentage = ((value / total) * 100).toFixed(2) + '%'; return context.label + ': ' + value + ' (' + percentage + ')'; }"
                        }
                    }
                }
            }
        }

    def generate_patient_chart(self):
        """Generate a simple chart with the total number of patients."""
        total_patients = PatientInformation.objects.count()

        return {
            "labels": ["Total Patients"],
            "datasets": [{
                "label": "Patients",
                "data": [total_patients],
                "backgroundColor": ["#36A2EB"],
                "borderColor": "#004C99",
                "borderWidth": 2,
            }],
        }

    def generate_patient_age_chart(self):
        """Generate a bar chart for patient age distribution."""
        patients = PatientInformation.objects.all()
        age_counts = {}

        today = date.today()
        for patient in patients:
            if patient.date_of_birth:
                age = today.year - patient.date_of_birth.year - (
                    (today.month, today.day) < (patient.date_of_birth.month, patient.date_of_birth.day)
                )
                age_counts[age] = age_counts.get(age, 0) + 1

        sorted_ages = sorted(age_counts.keys())
        sorted_counts = [age_counts[age] for age in sorted_ages]

        return {
            "labels": sorted_ages,
            "datasets": [{
                "label": "Patient Age Distribution",
                "data": sorted_counts,
                "backgroundColor": "#4CAF50",
                "borderColor": "#2E7D32",
                "borderWidth": 2,
            }],
        }

    def generate_patient_diagnosis_chart(self):
        """Generate a horizontal bar chart for patient diagnoses distribution."""
        diagnoses = PatientInformation.objects.values_list('diagnosis', flat=True)
        diagnosis_counts = {}

        for diagnosis in diagnoses:
            if diagnosis:
                diagnosis_counts[diagnosis] = diagnosis_counts.get(diagnosis, 0) + 1

        sorted_diagnoses = sorted(diagnosis_counts.keys(), key=lambda x: diagnosis_counts[x], reverse=True)
        sorted_counts = [diagnosis_counts[diag] for diag in sorted_diagnoses]

        return {
            "labels": sorted_diagnoses,
            "datasets": [{
                "label": "Diagnosis Distribution",
                "data": sorted_counts,
                "backgroundColor": "#36A2EB",
                "borderColor": "#004C99",
                "borderWidth": 2,
            }],
        }

    def generate_game_chart(self):
        """Generate a bar chart showing the most assigned games."""
        game_assignments = AssignedGame.objects.values("game__title").annotate(count=models.Count("game")).order_by("-count")

        labels = [entry["game__title"] for entry in game_assignments]
        data = [entry["count"] for entry in game_assignments]

        return {
            "labels": labels,
            "datasets": [{
                "label": "Game Assignments",
                "data": data,
                "backgroundColor": "#4CAF50",
                "borderColor": "#2E7D32",
                "borderWidth": 2,
            }],
        }

    def generate_appointment_trend_chart(self):
        """Generate a line chart showing the number of appointments per month."""
        today = date.today()
        start_date = today - timedelta(days=365)  # Show the past 12 months

        # Query appointments and count per month
        appointments = (
            Appointment.objects
            .filter(date__gte=start_date)
            .annotate(month=models.functions.TruncMonth("date"))
            .values("month")
            .annotate(count=Count("id"))
            .order_by("month")
        )

        # Extract labels (months) and data (counts)
        labels = [entry["month"].strftime("%b %Y") for entry in appointments]
        data = [entry["count"] for entry in appointments]

        return {
            "labels": labels,
            "datasets": [
                {
                    "label": "Appointments Per Month",
                    "data": data,
                    "borderColor": "#36A2EB",
                    "fill": "false",
                    "tension": 0.1,
                }
            ],
        }
        


    def get_charts_data(self):
        """Retrieve chart data for user groups."""
        return {
            "user_group_chart": self.generate_staff_chart(),
            "patient_chart": self.generate_patient_chart(),
            "game_assignment_chart": self.generate_game_chart(),
            "patient_age_chart": self.generate_patient_age_chart(),
            "patient_diagnosis_chart": self.generate_patient_diagnosis_chart(),
            "appointment_chart": self.generate_appointment_trend_chart(),
        }

    def dashboard_view(self, request):
        """Render the custom dashboard with all charts."""
        context = self.get_charts_data()
        return render(request, "admin/custom_dashboard.html", context)

    def get_urls(self):
        """Register the custom dashboard view in the Django admin panel."""
        urls = super().get_urls()
        custom_urls = [
            path("dashboard/", self.admin_view(self.dashboard_view), name="custom_admin_dashboard"),
        ]
        return custom_urls + urls

from simple_history.admin import SimpleHistoryAdmin
# Instantiate the custom admin site
custom_admin_site = CustomAdminSite(name="custom_admin")

# Register User and Group with custom_admin_site
custom_admin_site.register(User, UserAdmin)
custom_admin_site.register(Group, GroupAdmin)

# Register your models with the new admin site
custom_admin_site.register(TherapistInformation, SimpleHistoryAdmin)
custom_admin_site.register(AssistantInformation, SimpleHistoryAdmin)
custom_admin_site.register(GuardianInformation, SimpleHistoryAdmin)

custom_admin_site.register(PatientInformation)
custom_admin_site.register(PatientNotes)

custom_admin_site.register(Game)
custom_admin_site.register(AssignedGame)

custom_admin_site.register(EmailAddress)

custom_admin_site.register(Appointment)
custom_admin_site.register(AppointmentRequest)
