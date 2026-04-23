"""
Management command to load devices from inventory.json
"""
import json
import os
from django.core.management.base import BaseCommand
from apps.inventory.models import Device


class Command(BaseCommand):
    help = 'Load devices from inventory.json into the database'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='inventry.json',
            help='Path to the inventory JSON file'
        )
    
    def handle(self, *args, **options):
        """Load devices from JSON file"""
        json_file = options['file']
        
        # Check if file exists
        if not os.path.exists(json_file):
            self.stdout.write(
                self.style.ERROR(f"File not found: {json_file}")
            )
            return
        
        # Read JSON file
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            self.stdout.write(
                self.style.ERROR(f"Invalid JSON file: {str(e)}")
            )
            return
        
        inventory_data = data.get('inventory', {})
        created_count = 0
        skipped_count = 0
        error_count = 0
        
        device_type_mapping = {
            'laptops': 'laptop',
            'mouse': 'mouse',
            'keyboards': 'keyboard',
            'sim_cards': 'phone',
            'pc_setups': 'pc',
            'headphones': 'headphone',
        }
        
        # Process each device category
        for category, devices in inventory_data.items():
            device_type = device_type_mapping.get(category, 'other')
            
            if not isinstance(devices, list):
                continue
            
            for device_data in devices:
                try:
                    device_id = device_data.get('id')
                    
                    # Check if device already exists
                    if Device.objects.filter(device_id=device_id).exists():
                        self.stdout.write(
                            self.style.WARNING(f"Device {device_id} already exists - skipped")
                        )
                        skipped_count += 1
                        continue
                    
                    # Create device
                    device = Device.objects.create(
                        device_id=device_id,
                        name=self._get_device_name(category, device_data),
                        device_type=device_type,
                        brand=device_data.get('brand', 'Unknown'),
                        model=device_data.get('model', ''),
                        specifications=device_data,
                        status='available',
                    )
                    
                    self.stdout.write(
                        self.style.SUCCESS(f"Created device: {device_id} - {device.name}")
                    )
                    created_count += 1
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f"Error creating device {device_data.get('id')}: {str(e)}")
                    )
                    error_count += 1
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS(f"\n✓ Summary:")
        )
        self.stdout.write(f"  Created: {created_count} devices")
        if skipped_count > 0:
            self.stdout.write(
                self.style.WARNING(f"  Skipped: {skipped_count} devices (already exist)")
            )
        if error_count > 0:
            self.stdout.write(
                self.style.ERROR(f"  Errors: {error_count} devices")
            )
        
        self.stdout.write(
            self.style.SUCCESS("Done!")
        )
    
    def _get_device_name(self, category, device_data):
        """Generate device name from data"""
        if category == 'laptops':
            return f"{device_data.get('brand', '')} {device_data.get('model', '')}"
        elif category == 'mouse':
            return f"{device_data.get('brand', '')} {device_data.get('type', 'Mouse')}"
        elif category == 'keyboards':
            return f"{device_data.get('brand', '')} {device_data.get('type', 'Keyboard')}"
        elif category == 'headphones':
            return f"{device_data.get('brand', '')} {device_data.get('type', 'Headphone')}"
        elif category == 'sim_cards':
            return f"{device_data.get('provider', '')} SIM Card"
        elif category == 'pc_setups':
            return f"PC Setup - {device_data.get('processor', '')} {device_data.get('monitor', '')}"
        else:
            return device_data.get('name', device_data.get('id', 'Unknown Device'))
