from django.urls import path, include
from . import views

urlpatterns = [
    path('about-us/', views.AboutUsView.as_view(), name="about_us"),
    path('appointment/', views.AppointmentView.as_view(), name="appointment"),
    path('contact-us/', views.ContactUsView.as_view(), name="contact_us"),
    path('home/', views.HomeView.as_view(), name="home"),
    path('services/', views.ServicesView.as_view(), name="services"),
]