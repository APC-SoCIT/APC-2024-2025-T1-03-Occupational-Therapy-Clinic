from django.shortcuts import render
from django.views.generic import TemplateView
from appointments.views import create_appointment_request
# Create your views here.

class HomeView(TemplateView):
    template_name='home/home.html'
    
class AboutUsView(TemplateView):
    template_name='home/about_us.html'
    
class ContactUsView(TemplateView):
    template_name='home/contact_us.html'
    
class ServicesView(TemplateView):
    template_name='home/services.html'
    
class AppointmentView(TemplateView):
    template_name='home/appointment.html'