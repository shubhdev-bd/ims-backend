from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0003_inventoryasset"),
    ]

    operations = [
        migrations.AddField(
            model_name="assignment",
            name="cycle_images",
            field=models.JSONField(blank=True, default=list),
        ),
    ]
