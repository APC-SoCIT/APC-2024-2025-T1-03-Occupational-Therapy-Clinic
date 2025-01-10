from django.urls import path
from . import views

urlpatterns = [
    path('appointment/therapist/', views.therapist_dashboard, name='therapist_dashboard'),
    path('appointment/patient/', views.patient_dashboard, name='patient_dashboard'),
    path('appointment/list/', views.appointment_list, name='appointment_list'),
    path('appointment/create/', views.create_appointment, name='create_appointment'),
    path('appointment/<int:pk>/update/', views.update_appointment, name='update_appointment'),
    path('appointment/<int:pk>/delete/', views.delete_appointment, name='delete_appointment'),

    path('appointment/request/create/', views.create_appointment_request, name='create_appointment_request'),
    path('appointment/request/manage/', views.manage_appointment_requests, name='manage_appointment_requests'),
    path('appointment/request/<int:request_id>/update/', views.update_request_status, name='update_request_status'),

    path('recurring/create/', views.create_recurring_appointment, name='create_recurring_appointment'),
]


