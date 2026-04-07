"""
Migration to change profile_picture from ImageField to URLField
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_employee_hrms_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employee',
            name='profile_picture',
        ),
        migrations.AddField(
            model_name='employee',
            name='profile_picture_url',
            field=models.URLField(blank=True, help_text='URL to profile picture from Vercel Blob or similar', max_length=500, null=True),
        ),
    ]
