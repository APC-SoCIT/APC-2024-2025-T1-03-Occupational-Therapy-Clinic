from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.game_library, name='game_library'),
]
