"""
Management command to create test users for IMS system
"""
from django.core.management.base import BaseCommand, CommandError
from django.db import IntegrityError
from apps.authentication.models import Employee


class Command(BaseCommand):
    help = 'Create test users for IMS system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete existing test users before creating new ones',
        )

    def handle(self, *args, **options):
        test_users = [
            {
                'first_name': 'Arun',
                'last_name': 'Gautam',
                'email': 'arun.gautam@believersdestination.com',
                'password': 'TestPass@123',
                'department': 'IT',
                'role': 'employee',
            },
            {
                'first_name': 'Vikas',
                'last_name': 'Chauhan',
                'email': 'vikas.chauhan@believersdestination.com',
                'password': 'TestPass@123',
                'department': 'IT',
                'role': 'employee',
            },
            {
                'first_name': 'Vamika',
                'last_name': 'Singh',
                'email': 'vamika@believersdestination.com',
                'password': 'TestPass@123',
                'department': 'HR',
                'role': 'employee',
            },
            {
                'first_name': 'Shubh',
                'last_name': 'Saxena',
                'email': 'shubh.saxena@believersdestination.com',
                'password': 'TestPass@123',
                'department': 'IT',
                'role': 'employee',
            },
            {
                'first_name': 'Nikita',
                'last_name': 'Sharma',
                'email': 'nikita@believersdestination.com',
                'password': 'TestPass@123',
                'department': 'Operations',
                'role': 'employee',
            },
        ]

        if options['delete']:
            self.stdout.write(self.style.WARNING('Deleting existing test users...'))
            for user in test_users:
                try:
                    emp = Employee.objects.get(email=user['email'])
                    emp.delete()
                    self.stdout.write(self.style.WARNING(f"Deleted: {user['email']}"))
                except Employee.DoesNotExist:
                    pass

        self.stdout.write(self.style.SUCCESS('Creating test users...'))
        
        created_count = 0
        skipped_count = 0

        for user_data in test_users:
            email = user_data.pop('email')
            password = user_data.pop('password')
            
            try:
                employee = Employee.objects.get(email=email)
                self.stdout.write(
                    self.style.WARNING(f"User already exists: {email} (skipped)")
                )
                skipped_count += 1
                
            except Employee.DoesNotExist:
                try:
                    employee = Employee.objects.create_user(
                        email=email,
                        password=password,
                        **user_data
                    )
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"✓ Created: {employee.full_name} ({email}) | "
                            f"Employee ID: {employee.employee_id}"
                        )
                    )
                    created_count += 1
                    
                except IntegrityError as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error creating {email}: {str(e)}")
                    )

        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(
            self.style.SUCCESS(
                f'Summary: {created_count} created, {skipped_count} skipped'
            )
        )
        self.stdout.write(self.style.SUCCESS('='*60))
