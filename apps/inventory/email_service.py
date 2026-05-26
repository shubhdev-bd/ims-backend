"""
Email service for sending inventory notifications via Google Apps Script.
"""

import logging
from typing import List, Optional, Tuple, Union

import requests
from django.conf import settings
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger(__name__)


def _send_apps_script_request(payload):
    if not settings.APPS_SCRIPT_URL:
        logger.warning("Apps Script URL is not configured. Email will not be sent.")
        return {"success": False, "error": "Apps Script URL not configured"}

    payload = payload.copy()
    if settings.APPS_SCRIPT_API_KEY:
        payload.setdefault("api_key", settings.APPS_SCRIPT_API_KEY)
    if settings.DEFAULT_FROM_EMAIL:
        payload.setdefault("from_email", settings.DEFAULT_FROM_EMAIL)

    headers = {"Content-Type": "application/json"}
    if settings.APPS_SCRIPT_API_KEY:
        headers["Authorization"] = f"Bearer {settings.APPS_SCRIPT_API_KEY}"

    # Debug logging
    logger.info(
        f"Sending payload to Apps Script: to={payload.get('to')}, subject={payload.get('subject')}"
    )

    try:
        response = requests.post(
            settings.APPS_SCRIPT_URL,
            json=payload,
            headers=headers,
            timeout=20,
        )

        content_type = response.headers.get("content-type", "")
        if response.status_code != 200:
            logger.error(
                "Apps Script request failed with status %s: %s",
                response.status_code,
                response.text,
            )
            return {
                "success": False,
                "error": response.text,
                "status_code": response.status_code,
            }

        if content_type.startswith("application/json"):
            data = response.json()
            if not data.get("success", True):
                logger.error(
                    "Apps Script returned error: %s | Response: %s",
                    data.get("error", "Unknown error"),
                    data,
                )
            return data

        return {
            "success": True,
            "status_code": response.status_code,
            "message": "Email request sent successfully",
        }

    except requests.exceptions.RequestException as exc:
        logger.error("Apps Script email request failed: %s", exc)
        return {"success": False, "error": str(exc)}
    except Exception as exc:
        logger.error("Unexpected Apps Script email error: %s", exc)
        return {"success": False, "error": str(exc)}


class InventoryEmailService:
    """Inventory email notifications sent through Google Apps Script."""

    def _build_assignment_payload(self, assignment):
        if not assignment:
            return None, {"success": False, "error": "Assignment is required"}
        if not getattr(assignment, "employee", None):
            return None, {
                "success": False,
                "error": "Assignment has no employee attached",
            }
        if not getattr(assignment, "device", None):
            return None, {
                "success": False,
                "error": "Assignment has no device attached",
            }

        payload = {
            "employee_name": assignment.employee.full_name,
            "employee_email": assignment.employee.email,
            "device_name": assignment.device.name,
            "device_type": assignment.device.device_type,
            "serial_number": assignment.device.serial_number or "N/A",
            "assignment_id": str(assignment.id),
            "frontend_url": settings.FRONTEND_URL,
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
        mail_type: str = "send_email",
    ):
        recipients = self._normalize_recipients(to_emails)
        if not recipients:
            return None, {"success": False, "error": "No recipient email provided"}

        # Build payload WITH type field for Apps Script
        return {
            "type": mail_type,
            "to": ",".join(recipients),
            "to_emails": recipients,
            "subject": subject,
            "htmlBody": html_body or body,
            "textBody": body,
            "from_email": from_email or settings.DEFAULT_FROM_EMAIL,
        }, None

    def _send_django_email(self, subject, body, html_body, recipients, from_email):
        message = EmailMultiAlternatives(
            subject=subject,
            body=body,
            from_email=from_email,
            to=recipients,
        )
        if html_body and html_body != body:
            message.attach_alternative(html_body, "text/html")
        message.send(fail_silently=False)
        return {
            "success": True,
            "message": "Email sent via Django email backend",
            "fallback": True,
        }

    def send_generic_email(
        self,
        to_emails: Union[str, List[str]],
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        from_email: Optional[str] = None,
        mail_type: str = "send_email",
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
            logger.error(error["error"])
            return error

        result = _send_apps_script_request(payload)
        if not result.get("success"):
            error_message = result.get("error", "")
            logger.warning(
                "Apps Script generic email failed, falling back to Django email backend: %s",
                error_message,
            )
            try:
                return self._send_django_email(
                    subject,
                    body,
                    html_body or body,
                    self._normalize_recipients(to_emails),
                    from_email or settings.DEFAULT_FROM_EMAIL,
                )
            except Exception as exc:
                logger.error("Django email fallback failed: %s", exc)
                return {
                    "success": False,
                    "error": f"Email sending failed: {error_message} | Django fallback failed: {exc}",
                }

        return result

    def send_ticket_created_email(self, ticket):
        subject = f"New Ticket Submitted: {ticket.subject or ticket.ticket_number}"
        ticket_link = f"{settings.FRONTEND_URL}/tickets"
        html_body = f"""
        <p>Dear {ticket.requested_by.full_name},</p>
        <p>Your ticket has been submitted successfully.</p>
        <p><strong>Ticket Number:</strong> {ticket.ticket_number or ticket.id}</p>
        <p><strong>Subject:</strong> {ticket.subject}</p>
        <p><strong>Description:</strong> {ticket.description}</p>
        <p><strong>Priority:</strong> {ticket.priority}</p>
        <p>You can view your ticket in the IMS portal here: <a href="{ticket_link}">{ticket_link}</a></p>
        <p>Best regards,<br/>Inventory Management System</p>
        """
        text_body = (
            f"New ticket submitted: {ticket.subject or ticket.ticket_number}\n\n"
            f"{ticket.description}\n\n"
            f"Portal: {ticket_link}"
        )

        recipients = [ticket.requested_by.email]
        payload, error = self._build_email_payload(
            subject,
            text_body,
            recipients,
            html_body=html_body,
            mail_type="send_email",
        )
        if error:
            return error

        return _send_apps_script_request(payload)

    def send_ticket_assigned_email(self, ticket):
        assigned_to = ticket.assigned_to
        if not assigned_to or not ticket.requested_by:
            return {
                "success": False,
                "error": "Ticket assignment requires both assigned_to and requested_by",
            }

        subject = f"Ticket Assigned: {ticket.subject or ticket.ticket_number}"
        portal_link = f"{settings.FRONTEND_URL}/admin/ticketrequests"
        html_body = f"""
        <p>Dear {assigned_to.full_name},</p>
        <p>A ticket has been assigned to you.</p>
        <p><strong>Ticket Number:</strong> {ticket.ticket_number or ticket.id}</p>
        <p><strong>Subject:</strong> {ticket.subject}</p>
        <p><strong>Description:</strong> {ticket.description}</p>
        <p>Please review and update the ticket in the IMS portal here: <a href="{portal_link}">{portal_link}</a></p>
        <p>Best regards,<br/>Inventory Management System</p>
        """
        text_body = (
            f"Ticket assigned: {ticket.subject or ticket.ticket_number}\n\n"
            f"{ticket.description}\n\n"
            f"Portal: {portal_link}"
        )

        recipients = [assigned_to.email, ticket.requested_by.email]
        payload, error = self._build_email_payload(
            subject,
            text_body,
            recipients,
            html_body=html_body,
            mail_type="send_email",
        )
        if error:
            return error

        return _send_apps_script_request(payload)

    def send_ticket_resolved_email(self, ticket):
        if not ticket.requested_by:
            return {
                "success": False,
                "error": "Ticket must have a requester to send resolution email",
            }

        subject = f"Ticket Resolved: {ticket.subject or ticket.ticket_number}"
        ticket_link = f"{settings.FRONTEND_URL}/tickets"
        html_body = f"""
        <p>Dear {ticket.requested_by.full_name},</p>
        <p>Your ticket has been marked as resolved.</p>
        <p><strong>Ticket Number:</strong> {ticket.ticket_number or ticket.id}</p>
        <p><strong>Subject:</strong> {ticket.subject}</p>
        <p><strong>Description:</strong> {ticket.description}</p>
        <p>You can review it in the IMS portal here: <a href="{ticket_link}">{ticket_link}</a></p>
        <p>Best regards,<br/>Inventory Management System</p>
        """
        text_body = (
            f"Your ticket has been resolved: {ticket.subject or ticket.ticket_number}\n\n"
            f"{ticket.description}\n\n"
            f"Portal: {ticket_link}"
        )

        payload, error = self._build_email_payload(
            subject,
            text_body,
            ticket.requested_by.email,
            html_body=html_body,
            mail_type="send_email",
        )
        if error:
            return error

        return _send_apps_script_request(payload)

    def send_assignment_created_email(self, assignment):
        payload, error = self._build_assignment_payload(assignment)
        if error:
            logger.error(error["error"])
            return error

        payload["type"] = "assignment_created"
        return _send_apps_script_request(payload)

    def send_assignment_approved_email(self, assignment):
        payload, error = self._build_assignment_payload(assignment)
        if error:
            logger.error(error["error"])
            return error

        payload.update(
            {
                "type": "assignment_approved",
                "assigned_by": (
                    assignment.assigned_by.full_name
                    if assignment.assigned_by
                    else "Manager"
                ),
            }
        )
        return _send_apps_script_request(payload)

    def send_consent_request_email(self, assignment):
        payload, error = self._build_assignment_payload(assignment)
        if error:
            logger.error(error["error"])
            return error

        payload["type"] = "consent_requested"
        return _send_apps_script_request(payload)

    def send_assignment_processed_email(self, assignment, status, message):
        payload, error = self._build_assignment_payload(assignment)
        if error:
            logger.error(error["error"])
            return error

        payload.update(
            {
                "type": "assignment_processed",
                "status": status,
                "message": message,
            }
        )
        return _send_apps_script_request(payload)

    def send_consent_approved_email(self, assignment):
        payload, error = self._build_assignment_payload(assignment)
        if error:
            logger.error(error["error"])
            return error

        payload["type"] = "consent_approved"
        return _send_apps_script_request(payload)

    def send_device_grant_email(self, assignment, granted_by=None):
        if not assignment or not assignment.employee or not assignment.device:
            return {
                "success": False,
                "error": "Assignment with employee and device is required",
            }

        consent_link = f"{settings.FRONTEND_URL}/requesthistory"

        subject = f"Device Granted - {assignment.device.device_id}"
        html_body = f"""
        <p>Dear {assignment.employee.full_name},</p>
        <p>Your device request has been approved and a device has been granted to you.</p>
        <p><strong>Device ID:</strong> {assignment.device.device_id}</p>
        <p><strong>Device:</strong> {assignment.device.brand} {assignment.device.model}</p>
        <p><strong>Type:</strong> {assignment.device.device_type}</p>
        <p><strong>Granted By:</strong> {granted_by.full_name if granted_by else assignment.assigned_by.full_name if assignment.assigned_by else 'Admin'}</p>
        <p><strong>Expected Return Date:</strong> {assignment.expected_return_date or 'Not specified'}</p>
        <p>Please complete the undertaking and consent steps in the IMS portal:</p>
        <p>
          <a href="{consent_link}" style="display:inline-block;padding:10px 16px;background:#3b82f6;color:#fff;text-decoration:none;border-radius:6px;">
            Open IMS and Fill Consent
          </a>
        </p>
        <p>Best regards,<br/>Inventory Management System</p>
        """
        text_body = (
            f"Device granted: {assignment.device.device_id}\n"
            f"Device: {assignment.device.brand} {assignment.device.model}\n"
            f"Fill consent here: {consent_link}"
        )

        employee_result = self.send_generic_email(
            assignment.employee.email,
            subject,
            text_body,
            html_body=html_body,
        )

        admin_recipients = list(getattr(settings, "ADMIN_EMAIL_RECIPIENTS", []))
        if granted_by and granted_by.email:
            admin_recipients.append(granted_by.email)
        admin_recipients = sorted(set(admin_recipients))

        admin_result = {"success": True, "skipped": True}
        if admin_recipients:
            admin_subject = f"Device Grant Recorded - {assignment.employee.full_name}"
            admin_html = f"""
            <p>A device grant has been recorded in IMS.</p>
            <p><strong>Employee:</strong> {assignment.employee.full_name}</p>
            <p><strong>Employee Email:</strong> {assignment.employee.email}</p>
            <p><strong>Device ID:</strong> {assignment.device.device_id}</p>
            <p><strong>Device:</strong> {assignment.device.brand} {assignment.device.model}</p>
            <p><strong>Granted By:</strong> {granted_by.full_name if granted_by else assignment.assigned_by.full_name if assignment.assigned_by else 'Admin'}</p>
            """
            admin_text = (
                f"Device {assignment.device.device_id} granted to "
                f"{assignment.employee.full_name} ({assignment.employee.email})."
            )
            admin_result = self.send_generic_email(
                admin_recipients,
                admin_subject,
                admin_text,
                html_body=admin_html,
            )

        return {
            "success": employee_result.get("success", False)
            and admin_result.get("success", True),
            "employee_email": employee_result,
            "admin_email": admin_result,
        }

    def send_inventory_claim_email(self, inventory_asset):
        """Send claim request email for inventory asset via Apps Script"""
        if not inventory_asset.assigned_email:
            logger.warning(
                f"Cannot send claim email for asset {inventory_asset.id} - no email address"
            )
            return {"success": False, "error": "No email address for inventory asset"}

        subject = "Device Assignment - Action Required"
        asset_link = f"{settings.FRONTEND_URL}/mydevices"

        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #007bff; color: white; padding: 20px; border-radius: 5px 5px 0 0; }}
                .content {{ background-color: #f9f9f9; padding: 20px; border: 1px solid #ddd; }}
                .device-info {{ background-color: #fff; padding: 15px; border-left: 4px solid #007bff; margin: 20px 0; }}
                .device-info h3 {{ margin-top: 0; }}
                .button {{ display: inline-block; background-color: #007bff; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; margin-top: 15px; }}
                .footer {{ background-color: #f0f0f0; padding: 15px; text-align: center; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Device Assignment Notification</h1>
                </div>
                <div class="content">
                    <p>Dear <strong>{inventory_asset.assigned_person_name}</strong>,</p>
                    
                    <p>A company device has been assigned to you. Please review the details below and claim your device by logging into the IMS portal.</p>
                    
                    <div class="device-info">
                        <h3>Device Information</h3>
                        <table style="width: 100%; border-collapse: collapse;">
                            <tr style="border-bottom: 1px solid #ddd;">
                                <td style="padding: 8px; font-weight: bold; width: 30%;">Category:</td>
                                <td style="padding: 8px;">{inventory_asset.get_category_display()}</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #ddd;">
                                <td style="padding: 8px; font-weight: bold;">Device:</td>
                                <td style="padding: 8px;">{inventory_asset.asset_name}</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #ddd;">
                                <td style="padding: 8px; font-weight: bold;">Serial Number:</td>
                                <td style="padding: 8px;">{inventory_asset.serial_number}</td>
                            </tr>
                            <tr style="border-bottom: 1px solid #ddd;">
                                <td style="padding: 8px; font-weight: bold;">Assigned Date:</td>
                                <td style="padding: 8px;">{inventory_asset.assigned_date.strftime('%d-%m-%Y') if inventory_asset.assigned_date else 'N/A'}</td>
                            </tr>
                        </table>
                    </div>
                    
                    <p><strong>What you need to do:</strong></p>
                    <ol>
                        <li>Sign up or log in to the IMS portal</li>
                        <li>Go to "My Devices" section</li>
                        <li>Review your assigned device</li>
                        <li>Acknowledge receipt of the device</li>
                    </ol>
                    
                    <a href="{asset_link}" class="button">View My Devices →</a>
                    
                    <p style="margin-top: 20px; color: #666; font-size: 14px;">
                        If you did not expect this email or have questions about your device assignment, please contact the IT department.
                    </p>
                </div>
                <div class="footer">
                    <p>© Inventory Management System. This is an automated email, please do not reply.</p>
                </div>
            </div>
        </body>
        </html>
        """

        text_body = f"""
Device Assignment Notification

Dear {inventory_asset.assigned_person_name},

A company device has been assigned to you:

Category: {inventory_asset.get_category_display()}
Device: {inventory_asset.asset_name}
Serial Number: {inventory_asset.serial_number}
Assigned Date: {inventory_asset.assigned_date.strftime('%d-%m-%Y') if inventory_asset.assigned_date else 'N/A'}

Please sign up or log in to claim your device:
{asset_link}

Best regards,
Inventory Management System
        """

        # Build payload for Apps Script
        payload = {
            "type": "send_email",
            "to": inventory_asset.assigned_email,
            "subject": subject,
            "htmlBody": html_body,
            "textBody": text_body,
            "from_email": settings.DEFAULT_FROM_EMAIL,
        }

        result = _send_apps_script_request(payload)

        # Update asset to mark email as sent only if successful
        if result.get("success"):
            from django.utils import timezone

            inventory_asset.mail_sent = True
            inventory_asset.mail_sent_at = timezone.now()
            inventory_asset.save(update_fields=["mail_sent", "mail_sent_at"])
            logger.info(
                f"Inventory claim email sent successfully to {inventory_asset.assigned_email}"
            )

        return result


email_service = InventoryEmailService()
