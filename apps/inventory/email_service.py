"""
Email service for sending inventory notifications via Google Apps Script.
"""
import logging
from typing import List, Optional, Tuple, Union

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def _send_apps_script_request(payload):
    if not settings.APPS_SCRIPT_URL:
        logger.warning("Apps Script URL is not configured. Email will not be sent.")
        return {'success': False, 'error': 'Apps Script URL not configured'}

    payload = payload.copy()
    if settings.APPS_SCRIPT_API_KEY:
        payload.setdefault('api_key', settings.APPS_SCRIPT_API_KEY)
    if settings.DEFAULT_FROM_EMAIL:
        payload.setdefault('from_email', settings.DEFAULT_FROM_EMAIL)

    headers = {'Content-Type': 'application/json'}
    if settings.APPS_SCRIPT_API_KEY:
        headers['Authorization'] = f'Bearer {settings.APPS_SCRIPT_API_KEY}'

    try:
        response = requests.post(
            settings.APPS_SCRIPT_URL,
            json=payload,
            headers=headers,
            timeout=20,
        )

        content_type = response.headers.get('content-type', '')
        if response.status_code != 200:
            logger.error(
                "Apps Script request failed with status %s: %s",
                response.status_code,
                response.text,
            )
            return {
                'success': False,
                'error': response.text,
                'status_code': response.status_code,
            }

        if content_type.startswith('application/json'):
            data = response.json()
            if not data.get('success', True):
                logger.warning("Apps Script returned a non-success response: %s", data)
            return data

        return {
            'success': True,
            'status_code': response.status_code,
            'message': 'Email request sent successfully',
        }

    except requests.exceptions.RequestException as exc:
        logger.error("Apps Script email request failed: %s", exc)
        return {'success': False, 'error': str(exc)}
    except Exception as exc:
        logger.error("Unexpected Apps Script email error: %s", exc)
        return {'success': False, 'error': str(exc)}


class InventoryEmailService:
    """Inventory email notifications sent through Google Apps Script."""

    def _build_assignment_payload(self, assignment):
        if not assignment:
            return None, {'success': False, 'error': 'Assignment is required'}
        if not getattr(assignment, 'employee', None):
            return None, {'success': False, 'error': 'Assignment has no employee attached'}
        if not getattr(assignment, 'device', None):
            return None, {'success': False, 'error': 'Assignment has no device attached'}

        payload = {
            'employee_name': assignment.employee.full_name,
            'employee_email': assignment.employee.email,
            'device_name': assignment.device.name,
            'device_type': assignment.device.device_type,
            'serial_number': assignment.device.serial_number or 'N/A',
            'assignment_id': str(assignment.id),
            'frontend_url': settings.FRONTEND_URL,
        }
        return payload, None

    def _normalize_recipients(self, recipients: Union[str, List[str]]) -> List[str]:
        if isinstance(recipients, str):
            recipients = [recipients]
        return [email.strip() for email in recipients if email]

    def _build_email_payload(
        self,
        subject: str,
        body: str,
        to_emails: Union[str, List[str]],
        html_body: Optional[str] = None,
        from_email: Optional[str] = None,
        mail_type: str = 'send_email',
    ):
        recipients = self._normalize_recipients(to_emails)
        if not recipients:
            return None, {'success': False, 'error': 'No recipient email provided'}

        return {
            'type': mail_type,
            'to': ','.join(recipients),
            'to_emails': recipients,
            'subject': subject,
            'body': body,
            'htmlBody': html_body or body,
            'textBody': body,
            'from_email': from_email or settings.DEFAULT_FROM_EMAIL,
        }, None

    def send_generic_email(
        self,
        to_emails: Union[str, List[str]],
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        from_email: Optional[str] = None,
        mail_type: str = 'send_email',
    ):
        payload, error = self._build_email_payload(
            subject,
            body,
            to_emails,
            html_body=html_body,
            from_email=from_email,
            mail_type=mail_type,
        )
        if error:
            logger.error(error['error'])
            return error

        return _send_apps_script_request(payload)

    def send_ticket_created_email(self, ticket):
        subject = f"New Ticket Submitted: {ticket.subject or ticket.ticket_number}"
        html_body = f"""
        <p>Dear {ticket.requested_by.full_name},</p>
        <p>Your ticket has been submitted successfully.</p>
        <p><strong>Ticket Number:</strong> {ticket.ticket_number or ticket.id}</p>
        <p><strong>Subject:</strong> {ticket.subject}</p>
        <p><strong>Description:</strong> {ticket.description}</p>
        <p><strong>Priority:</strong> {ticket.priority}</p>
        <p>You can view your ticket in the IMS portal.</p>
        <p>Best regards,<br/>Inventory Management System</p>
        """
        text_body = f"New ticket submitted: {ticket.subject or ticket.ticket_number}\n\n{ticket.description}"

        recipients = [ticket.requested_by.email]
        payload, error = self._build_email_payload(
            subject,
            text_body,
            recipients,
            html_body=html_body,
            mail_type='send_email',
        )
        if error:
            return error

        return _send_apps_script_request(payload)

    def send_ticket_assigned_email(self, ticket):
        assigned_to = ticket.assigned_to
        if not assigned_to or not ticket.requested_by:
            return {'success': False, 'error': 'Ticket assignment requires both assigned_to and requested_by'}

        subject = f"Ticket Assigned: {ticket.subject or ticket.ticket_number}"
        html_body = f"""
        <p>Dear {assigned_to.full_name},</p>
        <p>A ticket has been assigned to you.</p>
        <p><strong>Ticket Number:</strong> {ticket.ticket_number or ticket.id}</p>
        <p><strong>Subject:</strong> {ticket.subject}</p>
        <p><strong>Description:</strong> {ticket.description}</p>
        <p>Please review and update the ticket in the IMS portal.</p>
        <p>Best regards,<br/>Inventory Management System</p>
        """
        text_body = f"Ticket assigned: {ticket.subject or ticket.ticket_number}\n\n{ticket.description}"

        recipients = [assigned_to.email, ticket.requested_by.email]
        payload, error = self._build_email_payload(
            subject,
            text_body,
            recipients,
            html_body=html_body,
            mail_type='send_email',
        )
        if error:
            return error

        return _send_apps_script_request(payload)

    def send_ticket_resolved_email(self, ticket):
        if not ticket.requested_by:
            return {'success': False, 'error': 'Ticket must have a requester to send resolution email'}

        subject = f"Ticket Resolved: {ticket.subject or ticket.ticket_number}"
        html_body = f"""
        <p>Dear {ticket.requested_by.full_name},</p>
        <p>Your ticket has been marked as resolved.</p>
        <p><strong>Ticket Number:</strong> {ticket.ticket_number or ticket.id}</p>
        <p><strong>Subject:</strong> {ticket.subject}</p>
        <p><strong>Description:</strong> {ticket.description}</p>
        <p>Best regards,<br/>Inventory Management System</p>
        """
        text_body = f"Your ticket has been resolved: {ticket.subject or ticket.ticket_number}\n\n{ticket.description}"

        payload, error = self._build_email_payload(
            subject,
            text_body,
            ticket.requested_by.email,
            html_body=html_body,
            mail_type='send_email',
        )
        if error:
            return error

        return _send_apps_script_request(payload)

    def send_assignment_created_email(self, assignment):
        payload, error = self._build_assignment_payload(assignment)
        if error:
            logger.error(error['error'])
            return error

        payload['type'] = 'assignment_created'
        return _send_apps_script_request(payload)

    def send_assignment_approved_email(self, assignment):
        payload, error = self._build_assignment_payload(assignment)
        if error:
            logger.error(error['error'])
            return error

        payload.update({
            'type': 'assignment_approved',
            'assigned_by': assignment.assigned_by.full_name if assignment.assigned_by else 'Manager',
        })
        return _send_apps_script_request(payload)

    def send_consent_request_email(self, assignment):
        payload, error = self._build_assignment_payload(assignment)
        if error:
            logger.error(error['error'])
            return error

        payload['type'] = 'consent_requested'
        return _send_apps_script_request(payload)

    def send_assignment_processed_email(self, assignment, status, message):
        payload, error = self._build_assignment_payload(assignment)
        if error:
            logger.error(error['error'])
            return error

        payload.update({
            'type': 'assignment_processed',
            'status': status,
            'message': message,
        })
        return _send_apps_script_request(payload)

    def send_consent_approved_email(self, assignment):
        payload, error = self._build_assignment_payload(assignment)
        if error:
            logger.error(error['error'])
            return error

        payload['type'] = 'consent_approved'
        return _send_apps_script_request(payload)


email_service = InventoryEmailService()
