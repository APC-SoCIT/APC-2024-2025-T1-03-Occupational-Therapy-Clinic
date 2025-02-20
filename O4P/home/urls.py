from django.urls import path, include
from . import views

urlpatterns = [
    path('about-us/', views.AboutUsView.as_view(), name="about_us"),
    path('appointment/', views.create_appointment_request, name="appointment"),
    path('contact-us/', views.ContactUsView.as_view(), name="contact_us"),
    path('', views.HomeView.as_view(), name="home"),
    path('services/', views.ServicesView.as_view(), name="services"),
]