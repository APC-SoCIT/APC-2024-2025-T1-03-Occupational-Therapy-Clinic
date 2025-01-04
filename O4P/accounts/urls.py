from django.urls import path, include

from . import views
from .views import TherapistSignupView, AssistantSignupView, GuardianSignupView

urlpatterns = [
    path('welcome/', views.WelcomeView.as_view(), name='welcome'),
    
    path("auth/signup/", views.RoleBasedSignupView.as_view(), name="account_signup"),
    path('auth/signup/therapist/', TherapistSignupView.as_view(), name='therapist_signup'),
    path('auth/signup/assistant/', AssistantSignupView.as_view(), name='assistant_signup'),
    path('auth/signup/guardian/', GuardianSignupView.as_view(), name='guardian_signup'),
]
