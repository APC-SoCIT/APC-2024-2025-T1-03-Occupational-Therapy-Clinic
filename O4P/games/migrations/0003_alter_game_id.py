# Generated by Django 5.1.4 on 2025-01-11 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('games', '0002_remove_game_free_to_play_game_game_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
