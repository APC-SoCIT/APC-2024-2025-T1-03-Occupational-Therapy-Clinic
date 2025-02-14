from django.urls import path, include
from . import views
from patients.views import AssignGameView, RemoveAssignedGameView

urlpatterns = [
    path('patients', views.PatientsListView.as_view(), name="patients.list"),
    path('patients/create/', views.PatientInformationCreateView.as_view(), name="patients.create"),
    path('patients/<int:pk>/', views.PatientDetailView.as_view(), name="patients.details"),
    
    path('patients/<int:pk>/edit/', views.PatientsUpdateView.as_view(), name="patients.update"),
    path('patients/<int:pk>/delete/', views.PatientsDeleteView.as_view(), name="patients.delete"),

    path('patients/notes/<int:pk>/', views.NoteDetailView.as_view(), name='notes.details'),
    path('patients/notes/<int:pk>/create/', views.NoteCreateView.as_view(), name='notes.create'),
    path('patients/notes/<int:pk>/edit', views.NotesUpdateView.as_view(), name="notes.update"),
    path('patients/notes/<int:pk>/delete', views.NotesDeleteView.as_view(), name="notes.delete"), 

    path('<int:patient_id>/assign_game/', AssignGameView.as_view(), name='assign_game'),
    path('<int:patient_id>/remove_assigned_game/<int:assigned_game_id>/', RemoveAssignedGameView.as_view(), name='remove_assigned_game'),
]