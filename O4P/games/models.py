from django.db import models

class Game(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    genre = models.CharField(max_length=50)
    description = models.TextField()
    release_date = models.DateField()
    developer = models.CharField(max_length=100)
    game_link = models.URLField(max_length=200, help_text="Enter the URL where the game is hosted")
    thumbnail = models.ImageField(upload_to='games/thumbnails/', null=True, blank=True)

    def __str__(self):
        return self.title
