"""
Signals for inventory assignment email notifications.
"""
import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Assignment, InventoryAsset
from .email_service import email_service

logger = logging.getLogger(__name__)


@receiver(pre_save, sender=Assignment)
def assignment_pre_save(sender, instance, **kwargs):
    if not instance.pk:
        return
    try:
        previous = Assignment.objects.get(pk=instance.pk)
        instance._previous_status = previous.status
        instance._previous_consent_approved = previous.consent_approved
    except Assignment.DoesNotExist:
        instance._previous_status = None
        instance._previous_consent_approved = None


@receiver(post_save, sender=Assignment)
def assignment_post_save(sender, instance, created, **kwargs):
    try:
        if created:
            email_service.send_assignment_created_email(instance)
            return

        previous_status = getattr(instance, '_previous_status', None)
        previous_consent_approved = getattr(instance, '_previous_consent_approved', None)

        if previous_status != instance.status:
            if instance.status == 'approved':
                email_service.send_assignment_approved_email(instance)
            elif instance.status == 'consent_pending':
                email_service.send_consent_request_email(instance)
            elif instance.status == 'returned':
                email_service.send_assignment_processed_email(
                    instance,
                    status='Returned',
                    message='Your device return has been recorded successfully. Thank you.',
                )

        if previous_consent_approved is False and instance.consent_approved:
            email_service.send_consent_approved_email(instance)
    except Exception as e:
        logger.error(f"Error in assignment_post_save signal: {e}")


@receiver(pre_save, sender=InventoryAsset)
def inventory_asset_pre_save(sender, instance, **kwargs):
    """Track previous state of inventory asset"""
    if not instance.pk:
        return
    try:
        previous = InventoryAsset.objects.get(pk=instance.pk)
        instance._previous_assigned_email = previous.assigned_email
    except InventoryAsset.DoesNotExist:
        instance._previous_assigned_email = None


@receiver(post_save, sender=InventoryAsset)
def inventory_asset_post_save(sender, instance, created, **kwargs):
    """Send claim email when assigned_email is updated"""
    try:
        # Check if email was updated
        previous_email = getattr(instance, '_previous_assigned_email', None)
        
        # Send email if:
        # 1. New asset with assigned_email
        # 2. Email was updated to a new value
        # 3. Email wasn't already sent (to avoid duplicates)
        if instance.assigned_email and not instance.mail_sent:
            if created or (previous_email != instance.assigned_email):
                if (
                    instance.requires_desk_number_for_claim()
                    and not instance.has_required_desk_number()
                ):
                    logger.info(
                        "Skipping claim email for PC asset %s until desk number is set",
                        instance.id,
                    )
                    return
                logger.info(
                    f"Sending inventory claim email to {instance.assigned_email} "
                    f"for asset {instance.asset_name} ({instance.serial_number})"
                )
                email_service.send_inventory_claim_email(instance)
    
    except Exception as e:
        logger.error(f"Error in inventory_asset_post_save signal: {e}")

    except Exception as exc:
        logger.error(f"Failed to send assignment email notification: {exc}")
