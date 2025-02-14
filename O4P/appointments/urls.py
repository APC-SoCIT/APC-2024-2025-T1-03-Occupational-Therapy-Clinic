from django.urls import path, include
from . import views
from django.contrib import admin

urlpatterns = [
    path('appointment/list/', views.appointment_list, name='appointment_list'),
    path('appointment/<int:appointment_id>/', views.appointment_detail, name='appointment_detail'),
    path('appointment/create/', views.create_appointment, name='create_appointment'),
    path('appointment/success/', views.appointment_success, name='appointment_success'),
    path('appointment/<int:pk>/update/', views.update_appointment, name='update_appointment'),
    path('appointment/<int:pk>/delete/', views.delete_appointment, name='delete_appointment'),
    path('appointment/request/create/', views.create_appointment_request, name='create_appointment_request'),
    path('appointment/manage/', views.manage_appointment_requests, name='manage_appointment_requests'),
    path('appointment/request/<int:request_id>/update/', views.update_request_status, name='update_request_status'),
    path('appointment/request/success', views.request_success, name='request_success'),


    path('appointment/recurring/create/', views.create_recurring_appointment, name='create_recurring_appointment'),

    path('appointment/calendar/api/', views.appointments_calendar_api, name='appointments_calendar_api'),
    #path('calendar/api/create/', views.create_appointment_api, name='create_appointment_api'),

    path('appointment/calendar/', views.calendar_view, name='calendar_view'),

    path('get_slots/<int:therapist_id>/', views.get_available_slots, name='get_available_slots'),

]

