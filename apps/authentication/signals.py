"""
Signals for authentication events.
Auto-links inventory assets when users sign up with matching emails.
"""
import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.authentication.models import Employee
from apps.inventory.models import InventoryAsset

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
        # Find all pending inventory assets with matching email
        pending_assets = InventoryAsset.objects.filter(
            assigned_email=instance.email,
            claimed=False,
            pending_claim=True,
            assigned_user__isnull=True
        )
        
        update_count = 0
        for asset in pending_assets:
            asset.assigned_user = instance
            asset.claimed = True
            asset.pending_claim = False
            asset.status = 'claimed'
            asset.save()
            update_count += 1
            
            logger.info(
                f"Auto-linked inventory asset {asset.id} ({asset.asset_name}) "
                f"to user {instance.email}"
            )
        
        if update_count > 0:
            logger.info(
                f"Auto-linked {update_count} inventory assets to user {instance.email}"
            )
    
    except Exception as e:
        logger.error(f"Error auto-linking inventory for user {instance.email}: {e}")
