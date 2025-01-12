# Generated by Django 5.1.2 on 2025-01-12 16:43

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='appointmentrequest',
            name='patient',
            field=models.ForeignKey(blank=True, limit_choices_to={'groups__name': 'Patient'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='appointment_requests', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='appointment',
            name='patient',
            field=models.ForeignKey(limit_choices_to={'groups__name': 'Patient'}, on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='appointmentrequest',
            name='contact_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='appointmentrequest',
            name='first_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='appointmentrequest',
            name='last_name',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
