"""
Management command to create initial test users
"""
from django.core.management.base import BaseCommand
from apps.authentication.models import Employee


class Command(BaseCommand):
    help = 'Create initial test users for the IMS system'
    
    def handle(self, *args, **options):
        """Create users"""
        users_data = [
            {
                'first_name': 'Arun',
                'last_name': 'Kumar Gautam',
                'email': 'arun@believersdestination.com',
                'password': 'password123',
                'role': 'employee',
                'department': 'IT',
            },
            {
                'first_name': 'Vikas',
                'last_name': 'Chauhan',
                'email': 'vikas@believersdestination.com',
                'password': 'password123',
                'role': 'employee',
                'department': 'IT',
            },
            {
                'first_name': 'Vamika',
                'last_name': '',
                'email': 'vamika@believersdestination.com',
                'password': 'password123',
                'role': 'employee',
                'department': 'HR',
            },
            {
                'first_name': 'Shubh',
                'last_name': 'Saxena',
                'email': 'shubh@believersdestination.com',
                'password': 'password123',
                'role': 'employee',
                'department': 'Finance',
            },
            {
                'first_name': 'Nikita',
                'last_name': '',
                'email': 'nikita@believersdestination.com',
                'password': 'password123',
                'role': 'employee',
                'department': 'Operations',
            },
        ]
        
        created_count = 0
        skipped_count = 0
        
        for user_data in users_data:
            email = user_data['email']
            
            # Check if employee already exists
            if Employee.objects.filter(email=email).exists():
                self.stdout.write(
                    self.style.WARNING(f"User {email} already exists - skipped")
                )
                skipped_count += 1
                continue
            
            # Create user
            password = user_data.pop('password')
            employee = Employee.objects.create_user(
                email=email,
                password=password,
                **user_data
            )
            
            self.stdout.write(
                self.style.SUCCESS(f"Successfully created user: {email} (ID: {employee.employee_id})")
            )
            created_count += 1
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS(f"\n✓ Created: {created_count} users")
        )
        if skipped_count > 0:
            self.stdout.write(
                self.style.WARNING(f"⚠ Skipped: {skipped_count} users (already exist)")
            )
        
        self.stdout.write(
            self.style.SUCCESS("Done!")
        )
