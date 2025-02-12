from django.urls import path, include

from . import views
from .views import TherapistSignupView, AssistantSignupView, GuardianSignupView
from .views import GuardianListView, AssistantListView, TherapistListView
from .views import AssistantDetailView, TherapistDetailView, GuardianDetailView
from .views import GuardianUpdateView, GuardianDeleteView, AssistantUpdateView, AssistantDeleteView, TherapistUpdateView, TherapistDeleteView
from .views import get_municipalities

urlpatterns = [
    path('welcome/', views.WelcomeView.as_view(), name='welcome'),
    
    
    path('auth/signup/therapist/', TherapistSignupView.as_view(), name='therapist_signup'),
    path('auth/signup/assistant/', AssistantSignupView.as_view(), name='assistant_signup'),
    path('auth/signup/', GuardianSignupView.as_view(), name='guardian_signup'),
    
    path('get-municipalities/', get_municipalities, name='get_municipalities'),
     
    path('roles/guardian/list', GuardianListView.as_view(), name='guardian_list'),
    path('roles/assistant/list', AssistantListView.as_view(), name='assistant_list'),
    path('roles/therapist/list', TherapistListView.as_view(), name='therapist_list'),
    
    path('roles/assistant/<int:pk>/', AssistantDetailView.as_view(), name='assistant_detail'),
    path('roles/therapist/<int:pk>/', TherapistDetailView.as_view(), name='therapist_detail'),
    path('roles/guardian/<int:pk>/', GuardianDetailView.as_view(), name='guardian_detail'),
    
    path('roles/guardian/<int:pk>/edit', GuardianUpdateView.as_view(), name='guardian_edit'),
    path('roles/assistant/<int:pk>/edit', AssistantUpdateView.as_view(), name='assistant_edit'),
    path('roles/therapist/<int:pk>/edit', TherapistUpdateView.as_view(), name='therapist_edit'),
    
    path('roles/guardian/<int:pk>/delete', GuardianDeleteView.as_view(), name='guardian_delete'),
    path('roles/assistant/<int:pk>/delete', AssistantDeleteView.as_view(), name='assistant_delete'),
    path('roles/therapist/<int:pk>/delete', TherapistDeleteView.as_view(), name='therapist_delete'),
]
