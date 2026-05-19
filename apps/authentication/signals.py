"""
Signals for authentication events.
Auto-links inventory assets when users sign up with matching emails.
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.authentication.models import Employee
from apps.inventory.models import link_inventory_assets_for_employee

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Employee)
def employee_post_save(sender, instance, created, **kwargs):
    """
    When an employee signs up, auto-link any pending inventory assets
    with matching email addresses
    """
    if not created:
        return  # Only process on creation
    
    if not instance.email:
        return
    
    try:
        linked_assets = link_inventory_assets_for_employee(instance)
        linked_count = linked_assets.count()

        if linked_count > 0:
            logger.info(
                "Linked %s inventory assets to user %s for claim review",
                linked_count,
                instance.email,
            )
    
    except Exception as e:
        logger.error(f"Error auto-linking inventory for user {instance.email}: {e}")
