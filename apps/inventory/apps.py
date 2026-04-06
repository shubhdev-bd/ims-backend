from django.apps import AppConfig


class InventoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.inventory'

    def ready(self):
        # Import inventory signals to ensure email notifications are wired
        import apps.inventory.signals  # noqa
