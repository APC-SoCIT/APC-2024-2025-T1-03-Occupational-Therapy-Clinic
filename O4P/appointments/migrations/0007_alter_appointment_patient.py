# Generated by Django 5.1.2 on 2025-02-10 06:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0006_alter_appointmentrequest_therapist'),
        ('patients', '0002_patientinformation_relationship_to_guardian'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appointment',
            name='patient',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='appointments', to='patients.patientinformation'),
        ),
    ]
