from django.urls import path, include
from . import views

urlpatterns = [
    path('patients', views.PatientsListView.as_view(), name="patients.list"),
    path('patients/<int:pk>/', views.PatientDetailView.as_view(), name="patients.details"),
    path('patients/<int:pk>/edit/', views.PatientsUpdateView.as_view(), name="patients.update"),
    path('patients/<int:pk>/delete/', views.PatientsDeleteView.as_view(), name="patients.delete"),
]