from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="devicerequest",
            name="status",
            field=models.CharField(
                choices=[
                    ("pending", "Pending"),
                    ("consent_pending", "Consent Pending"),
                    ("active", "Active"),
                    ("returned", "Returned"),
                    ("rejected", "Rejected"),
                ],
                default="pending",
                max_length=20,
            ),
        ),
    ]
