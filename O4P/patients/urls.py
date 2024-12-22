from django.urls import path, include
from . import views
from .views import RoleBasedSignupView

urlpatterns = [
    path('patients', views.PatientsListView.as_view(), name="patients.list"),
    path('patients/<int:pk>/', views.PatientDetailView.as_view(), name="patients.details"),
    path('patients/<int:pk>/edit/', views.PatientsUpdateView.as_view(), name="patients.update"),
    path('patients/<int:pk>/delete/', views.PatientsDeleteView.as_view(), name="patients.delete"),

    path('patients/notes/<int:pk>/', views.NoteDetailView.as_view(), name='notes.details'),
    path('patients/notes/<int:pk>/create/', views.NoteCreateView.as_view(), name='notes.create'),
    path('patients/notes/<int:pk>/edit', views.NotesUpdateView.as_view(), name="notes.update"),
    path('patients/notes/<int:pk>/delete', views.NotesDeleteView.as_view(), name="notes.delete"), 
]