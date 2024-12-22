from django.urls import path, include

from . import views


urlpatterns = [
    path('welcome/', views.WelcomeView.as_view(), name='welcome'),
    path("auth/signup/", views.RoleBasedSignupView.as_view(), name="account_signup")
]
