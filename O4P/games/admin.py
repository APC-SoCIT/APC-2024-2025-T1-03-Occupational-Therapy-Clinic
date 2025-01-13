<<<<<<< HEAD
from django.contrib import admin
from .models import Game

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'genre', 'developer', 'release_date', 'game_link', 'thumbnail')
    search_fields = ('title', 'genre', 'developer')
    list_filter = ('genre',)
    ordering = ('release_date', 'title')
=======
from django.contrib import admin

# Register your models here.
>>>>>>> 44cd0bcf56d261caee180073fa4ccf68ac1bb560
