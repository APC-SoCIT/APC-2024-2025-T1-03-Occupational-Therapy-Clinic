from django.contrib import admin
from .models import Game, AssignedGame

@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'genre', 'developer', 'release_date', 'game_link', 'thumbnail')
    search_fields = ('title', 'genre', 'developer')
    list_filter = ('genre',)
    ordering = ('release_date', 'title')

@admin.register(AssignedGame)
class AssignedGameAdmin(admin.ModelAdmin):
    list_display = ('patient', 'game', 'assigned_date')
    search_fields = ('patient__first_name', 'patient__last_name', 'game__name')