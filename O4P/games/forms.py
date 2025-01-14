from django import forms
from .models import Game

class GameForm(forms.ModelForm):
    class Meta:
        model = Game
        fields = ['title', 'genre', 'description', 'release_date', 'developer', 'game_link', 'thumbnail']  # Include the 'thumbnail' field
        labels = {
            'title': 'Game Title',
            'genre': 'Genre',
            'description': 'Description',
            'release_date': 'Release Date',
            'developer': 'Developer',
            'game_link': 'Game Link',
            'thumbnail': 'Thumbnail Image',  # Add a label for the thumbnail field
        }
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'genre': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'release_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'developer': forms.TextInput(attrs={'class': 'form-control'}),
            'game_link': forms.URLInput(attrs={'class': 'form-control'}),
            'thumbnail': forms.ClearableFileInput(attrs={'class': 'form-control'}),  # Add a widget for file input
        }