from django.db import migrations


def load_devices(apps, schema_editor):
    # use loaddata to import fixtures
    from django.core.management import call_command
    try:
        call_command('loaddata', 'devices.json')
    except Exception as e:
        # migrate should not fail if data already exists
        print(f"Warning: could not load device fixtures: {e}")


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(load_devices),
    ]
