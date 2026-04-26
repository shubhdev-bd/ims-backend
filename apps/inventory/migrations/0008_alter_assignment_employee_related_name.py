from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0007_devicerequest_assignment'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignment',
            name='employee',
            field=models.ForeignKey(
                on_delete=models.CASCADE,
                related_name='assignments',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
