from django.db import models, migrations

def apply_migration(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.bulk_create([
        Group(name=u'Patient'),
        Group(name=u'Guardian'),
        Group(name=u'Assistant'),
        Group(name=u'Therapist'),
        Group(name=u'Administrator'),
    ])

def revert_migration(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    Group.objects.filter(
        name__in=[
            u'Patient',
            u'Guardian',
            u'Assistant',
            u'Therapist',
            u'Administrator'
        ]
    ).delete()

class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.RunPython(apply_migration, revert_migration)
    ]
