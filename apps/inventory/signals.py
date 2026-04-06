"""
Signals for inventory assignment email notifications.
"""
import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Assignment
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
                    message='Your device has been returned and is pending review.',
                )

        if previous_consent_approved is False and instance.consent_approved:
            email_service.send_consent_approved_email(instance)

    except Exception as exc:
        logger.error(f"Failed to send assignment email notification: {exc}")
