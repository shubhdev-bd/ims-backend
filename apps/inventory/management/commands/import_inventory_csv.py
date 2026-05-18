"""
Management command to import inventory from CSV files
Usage: python manage.py import_inventory_csv <file_path> [--category CATEGORY]
"""
from django.core.management.base import BaseCommand, CommandError
from apps.inventory.csv_import_service import CSVImportService, CSVImportError
import os


class Command(BaseCommand):
    help = 'Import inventory assets from CSV file'
    
    def add_arguments(self, parser):
        parser.add_argument(
            'file_path',
            type=str,
            help='Path to CSV file'
        )
        parser.add_argument(
            '--category',
            type=str,
            default=None,
            help='Category (pc, laptop, headphone, connector, mobile)'
        )
    
    def handle(self, *args, **options):
        file_path = options['file_path']
        category = options.get('category')
        
        # Validate file exists
        if not os.path.exists(file_path):
            raise CommandError(f"File not found: {file_path}")
        
        # Check file extension
        if not file_path.lower().endswith('.csv'):
            raise CommandError("File must be a CSV file")
        
        try:
            self.stdout.write(f"Importing from: {file_path}")
            if category:
                self.stdout.write(f"Category: {category}")
            
            # Run import
            service = CSVImportService(category=category)
            results = service.import_from_file(file_path)
            
            # Print results
            self.stdout.write(self.style.SUCCESS('✓ Import completed!'))
            self.stdout.write(f"  Created: {results['created']}")
            self.stdout.write(f"  Skipped: {results['skipped']}")
            self.stdout.write(f"  Errors: {results['errors']}")
            self.stdout.write(f"  Total: {results['total']}")
            
            if results['error_details']:
                self.stdout.write(self.style.WARNING('\n⚠ Errors:'))
                for error in results['error_details']:
                    self.stdout.write(f"  - {error}")
        
        except CSVImportError as e:
            raise CommandError(f"Import failed: {str(e)}")
        except Exception as e:
            raise CommandError(f"Unexpected error: {str(e)}")
