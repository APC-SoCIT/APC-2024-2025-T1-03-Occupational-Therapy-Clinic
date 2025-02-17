# Generated by Django 5.1.2 on 2025-02-15 07:15

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0002_initial'),
        ('appointments', '0001_initial'),
        ('patients', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='patient',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='patients.patientinformation'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='therapist',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='therapist_appointments', to='accounts.therapistinformation'),
        ),
        migrations.AddField(
            model_name='appointmentrequest',
            name='therapist',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='appointment_requests', to='accounts.therapistinformation'),
        ),
        migrations.AddField(
            model_name='recurringappointment',
            name='patient',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recurring_appointments', to='patients.patientinformation'),
        ),
        migrations.AddField(
            model_name='recurringappointment',
            name='therapist',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='therapist_recurring_appointments', to='accounts.therapistinformation'),
        ),
    ]
