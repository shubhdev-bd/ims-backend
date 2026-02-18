from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decouple import config

class Command(BaseCommand):
    help = "Create superuser automatically from env vars"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        email = config("SUPERUSER_EMAIL", default="")
        password = config("SUPERUSER_PASSWORD", default="")
        first_name = config("SUPERUSER_FIRST_NAME", default="Admin")
        last_name = config("SUPERUSER_LAST_NAME", default="User")

        if not email or not password:
            self.stdout.write(
                "SUPERUSER_EMAIL or SUPERUSER_PASSWORD not set — skipping."
            )
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write(
                f"Superuser {email} already exists — skipping."
            )
            return

        User.objects.create_superuser(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        self.stdout.write(
            self.style.SUCCESS(f"Superuser {email} created successfully!")
        )
