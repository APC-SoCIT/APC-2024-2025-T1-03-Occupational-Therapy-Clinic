from django.db import models, migrations

def apply_migration(apps, schema_editor):
    Group = apps.get_model('auth', 'Group')
    
    groups_to_create = [
        'Patient', 'Guardian', 'Assistant', 'Therapist', 'Administrator'
    ]
    
    for group_name in groups_to_create:
        if not Group.objects.filter(name=group_name).exists():
            Group.objects.create(name=group_name)

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
