# views.py
from django.shortcuts import render

def game_library(request):
    games = [
        {"id": 1, "name": "Game 1", "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor..."},
        {"id": 2, "name": "Game 2", "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor..."},
        {"id": 3, "name": "Game 3", "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor..."},
        {"id": 4, "name": "Game 4", "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor..."},
        {"id": 5, "name": "Game 5", "description": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor..."},
    ]
    return render(request, 'games/game_library.html', {'games': games})