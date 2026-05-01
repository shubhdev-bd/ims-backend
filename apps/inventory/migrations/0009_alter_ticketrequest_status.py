from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0008_alter_assignment_employee_related_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticketrequest',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('approved', 'Approved'),
                    ('on_repair', 'Repairing Initiated'),
                    ('repaired', 'Repaired'),
                    ('rejected', 'Rejected'),
                    ('in_progress', 'Legacy: In Progress'),
                    ('resolved', 'Legacy: Resolved'),
                    ('closed', 'Legacy: Closed'),
                ],
                default='pending',
                max_length=20,
            ),
        ),
    ]
