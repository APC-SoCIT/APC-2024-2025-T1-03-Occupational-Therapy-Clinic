from django.urls import path, include

from . import views

urlpatterns = [
    path('welcome/', views.WelcomeView.as_view(), name='welcome'),
    path('login/', views.LoginInterfaceView.as_view(), name='login'),
    path('logout/', views.LogoutInterfaceView.as_view(), name='logout'),
    path('patients/new', views.SignupView.as_view(), name="patients.new"),
]
