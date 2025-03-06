from django.urls import path
from .views import list_schedule, create_schedule, update_schedule, delete_schedule

urlpatterns = [
    path('therapist/schedule/', list_schedule, name='list_schedule'),
    path('therapist/schedule/create/', create_schedule, name='create_schedule'),
    path('therapist/schedule/update/<int:slot_id>/', update_schedule, name='update_schedule'),
    path('therapist/schedule/delete/<int:slot_id>/', delete_schedule, name='delete_schedule'),
]