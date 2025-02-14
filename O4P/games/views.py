from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Game, AssignedGame
from .forms import GameForm  # Import the form for handling games
from patients.models import PatientInformation  # Import PatientInformation for patient data

# General view for displaying the game library
def game_library(request):
    query = request.GET.get('q')
    games = Game.objects.all().order_by('id')
    
    if query:
        games = games.filter(title__icontains=query)
    
    # Filter games by developer
    abcya_games = Game.objects.filter(developer="ABCya").order_by('id')
    quartize_games = Game.objects.filter(developer="Quartize").order_by('id')

    assigned_games_by_patient = {}
    if request.user.groups.filter(name='Guardian').exists():
        patients = PatientInformation.objects.filter(account_id=request.user)
        for patient in patients:
            assigned_games = AssignedGame.objects.filter(patient=patient)
            if assigned_games.exists():
                assigned_games_by_patient[patient] = assigned_games

    context = {
        'games': games,
        'abcya_games': abcya_games,
        'quartize_games': quartize_games,
        'assigned_games_by_patient': assigned_games_by_patient,
    }
    return render(request, 'games/game_library.html', context)

@login_required
def admin_game_library(request):
    if not request.user.is_superuser:
        return render(request, 'games/unauthorized.html', status=403)
    games = Game.objects.all().order_by('id')  # Admin-specific game library with all games
    return render(request, 'games/admin_game_library.html', {'games': games})

@login_required
def add_game(request):
    if not request.user.is_superuser:
        return HttpResponse("Unauthorized", status=403)
    if request.method == "POST":
        form = GameForm(request.POST, request.FILES)  # Include request.FILES
        if form.is_valid():
            thumbnail = request.FILES.get('thumbnail')
            if thumbnail and not thumbnail.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                form.add_error('thumbnail', "Upload failed. Make sure the file is JPEG or PNG.")
                return render(request, 'games/game_form.html', {'form': form})
            form.save()  # Save the new game to the database
            return redirect('admin_game_library')  # Redirect to admin game library after adding
    else:
        form = GameForm()
    return render(request, 'games/game_form.html', {'form': form})

@login_required
def edit_game(request, game_id):
    if not request.user.is_superuser:
        return HttpResponse("Unauthorized", status=403)
    # Fetch the game object or return 404
    game = get_object_or_404(Game, id=game_id)
    if request.method == "POST":
        form = GameForm(request.POST, request.FILES, instance=game)  # Include request.FILES
        if form.is_valid():
            thumbnail = request.FILES.get('thumbnail')
            if thumbnail and not thumbnail.name.lower().endswith(('.jpg', '.jpeg', '.png')):
                form.add_error('thumbnail', "Upload failed. Make sure the file is JPEG or PNG.")
                return render(request, 'games/game_form.html', {'form': form})
            form.save()  # Save the updated game
            return redirect('admin_game_library')  # Redirect to admin game library after editing
    else:
        form = GameForm(instance=game)
    return render(request, 'games/game_form.html', {'form': form})

@login_required
def delete_game(request, game_id):
    if not request.user.is_superuser:
        return HttpResponse("Unauthorized", status=403)
    # Fetch the game object or return 404
    game = get_object_or_404(Game, id=game_id)
    if request.method == "POST":
        # Handle game deletion logic
        game.delete()
        return redirect('admin_game_library')  # Redirect to admin game library
    return render(request, 'games/game_confirm_delete.html', {'game': game})
