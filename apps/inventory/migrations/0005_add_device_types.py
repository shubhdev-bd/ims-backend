"""
Migration to add new device types
Note: This migration documents the addition of new device types:
- cable
- charger
- pc
- headphone  
- keyboard
- pendrive
- hard_drive
- accessories

Since these are just choices on the device_type CharField, no database changes are required.
"""
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_device_image_url'),
    ]

    operations = [
        # Empty migration - choices don't require database changes
    ]
