# Generated by Django 5.1.2 on 2025-02-09 08:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('therapists', '0003_alter_availableday_unique_together'),
    ]

    operations = [
        migrations.CreateModel(
            name='AvailableSlot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(choices=[('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'), ('thursday', 'Thursday'), ('friday', 'Friday'), ('saturday', 'Saturday'), ('sunday', 'Sunday')], max_length=10)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('therapist', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='available_slots', to='therapists.therapist')),
            ],
            options={
                'unique_together': {('therapist', 'day', 'start_time', 'end_time')},
            },
        ),
        migrations.DeleteModel(
            name='AvailableDay',
        ),
    ]
