from django.shortcuts import render

def game_library(request):
    # Sample data for games
    games = [
        {'title': 'Game 1', 'description': 'Fun puzzle game', 'image_url': 'path/to/image1.jpg'},
        {'title': 'Game 2', 'description': 'Exciting adventure game', 'image_url': 'path/to/image2.jpg'},
        {'title': 'Game 3', 'description': 'Strategic card game', 'image_url': 'path/to/image3.jpg'},
    ]
    return render(request, 'games/game_library.html', {'games': games})