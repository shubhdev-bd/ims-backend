from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inventory", "0005_assignment_return_request_pending_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="inventoryasset",
            name="desk_number",
            field=models.CharField(
                blank=True,
                db_index=True,
                max_length=100,
                null=True,
            ),
        ),
    ]
