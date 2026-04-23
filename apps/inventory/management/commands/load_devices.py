"""
Management command to load devices from inventory.json
"""
import json
import os
from django.core.management.base import BaseCommand, CommandError
from apps.inventory.models import Device


class Command(BaseCommand):
    help = 'Load devices from inventory.json file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='inventry.json',
            help='Path to inventory JSON file (default: inventry.json in project root)',
        )
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete existing devices before loading',
        )

    def handle(self, *args, **options):
        file_path = options['file']

        # If relative path, look in project root
        if not os.path.isabs(file_path):
            file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(
                os.path.dirname(os.path.dirname(__file__))))), file_path)

        if not os.path.exists(file_path):
            raise CommandError(f'File not found: {file_path}')

        if options['delete']:
            self.stdout.write(self.style.WARNING('Deleting existing devices...'))
            Device.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('All devices deleted.'))

        self.stdout.write(self.style.SUCCESS(f'Loading devices from: {file_path}'))

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise CommandError(f'Invalid JSON file: {str(e)}')

        created_count = 0
        skipped_count = 0

        inventory = data.get('inventory', {})

        # Device type mapping
        device_type_mapping = {
            'laptops': 'laptop',
            'desktops': 'desktop',
            'pc_setups': 'pc',
            'monitors': 'monitor',
            'keyboards': 'keyboard',
            'mouse': 'mouse',
            'headsets': 'headset',
            'headphones': 'headphone',
            'phones': 'phone',
            'tablets': 'tablet',
            'cables': 'cable',
            'chargers': 'charger',
            'pendrives': 'pendrive',
            'hard_drives': 'hard_drive',
            'sim_cards': 'phone',  # Treat SIM cards as phone
            'accessories': 'accessories',
        }

        for category_key, devices_list in inventory.items():
            if not isinstance(devices_list, list):
                continue

            device_type = device_type_mapping.get(category_key, 'other')

            for device_data in devices_list:
                device_id = device_data.get('id')
                
                if not device_id:
                    self.stdout.write(
                        self.style.WARNING(f'Skipping device without ID in {category_key}')
                    )
                    skipped_count += 1
                    continue

                try:
                    device = Device.objects.get(device_id=device_id)
                    self.stdout.write(
                        self.style.WARNING(f'Device already exists: {device_id} (skipped)')
                    )
                    skipped_count += 1
                    continue

                except Device.DoesNotExist:
                    pass

                # Create device name from available fields
                device_name = self._create_device_name(device_data, category_key)

                try:
                    # Extract quantity (default to 1)
                    quantity = device_data.get('quantity', 1)
                    
                    # Create device record (for now just 1, quantity is informational)
                    device = Device.objects.create(
                        device_id=device_id,
                        name=device_name,
                        device_type=device_type,
                        brand=device_data.get('brand', 'Unknown'),
                        model=device_data.get('model', 'Unknown'),
                        serial_number=device_data.get('serial_number', ''),
                        status='available',
                        condition='new',
                        specifications=self._extract_specifications(device_data, category_key),
                        notes=f'Quantity available: {quantity}',
                    )

                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Created: {device_name} ({device_id}) | Type: {device_type}'
                        )
                    )
                    created_count += 1

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'Error creating {device_id}: {str(e)}')
                    )
                    skipped_count += 1

        self.stdout.write(self.style.SUCCESS('\n' + '='*60))
        self.stdout.write(
            self.style.SUCCESS(
                f'Summary: {created_count} created, {skipped_count} skipped'
            )
        )
        self.stdout.write(self.style.SUCCESS('='*60))

    def _create_device_name(self, device_data, category_key):
        """Create a device name from available fields"""
        if 'name' in device_data:
            return device_data['name']
        
        brand = device_data.get('brand', '')
        model = device_data.get('model', '')
        device_type = device_data.get('type', '')

        parts = [p for p in [brand, model, device_type] if p]
        return ' '.join(parts) if parts else f"{category_key.rstrip('s')} Device"

    def _extract_specifications(self, device_data, category_key):
        """Extract specifications based on device category"""
        specs = {}

        # Common fields to extract
        spec_fields = [
            'processor', 'ram', 'storage', 'color', 'weight', 'screen_size',
            'battery_life', 'connectivity', 'type', 'provider', 'capacity'
        ]

        for field in spec_fields:
            if field in device_data:
                specs[field] = str(device_data[field])

        return specs
