"""
Authentication Utility Functions
"""
import secrets
import requests
from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from .models import PasswordResetToken


def generate_reset_token():
    """Generate a secure random token"""
    return secrets.token_urlsafe(32)


def create_password_reset_token(employee):
    """Create a password reset token for employee"""
    # Invalidate any existing tokens
    PasswordResetToken.objects.filter(
        employee=employee,
        is_used=False
    ).update(is_used=True)
    
    # Create new token
    token = generate_reset_token()
    expires_at = timezone.now() + timedelta(hours=24)
    
    reset_token = PasswordResetToken.objects.create(
        employee=employee,
        token=token,
        expires_at=expires_at
    )
    
    return reset_token


def send_email_via_apps_script(to_email, subject, html_content, text_content=None):
    """
    Send email using Google Apps Script Web App
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML content of email
        text_content: Plain text content (optional)
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    if not settings.APPS_SCRIPT_URL:
        print(f"Apps Script URL not configured. Email would be sent to: {to_email}")
        print(f"Subject: {subject}")
        print(f"Content: {html_content}")
        return True  # Return True in development
    
    try:
        payload = {
            'to': to_email,
            'subject': subject,
            'htmlBody': html_content,
        }
        
        if text_content:
            payload['textBody'] = text_content
        
        # Add API key if configured
        headers = {}
        if settings.APPS_SCRIPT_API_KEY:
            headers['Authorization'] = f'Bearer {settings.APPS_SCRIPT_API_KEY}'
        
        response = requests.post(
            settings.APPS_SCRIPT_URL,
            json=payload,
            headers=headers,
            timeout=10
        )
        
        if response.status_code == 200:
            return True
        else:
            print(f"Failed to send email: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"Error sending email via Apps Script: {str(e)}")
        return False


def send_welcome_email(employee):
    """Send welcome email to new employee"""
    subject = "Welcome to Inventory Management System"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
            .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Welcome to IMS!</h1>
            </div>
            <div class="content">
                <p>Hi {employee.first_name},</p>
                <p>Welcome to the Inventory Management System! Your account has been successfully created.</p>
                
                <p><strong>Your Details:</strong></p>
                <ul>
                    <li>Email: {employee.email}</li>
                    <li>Employee ID: {employee.employee_id}</li>
                    <li>Department: {employee.get_department_display()}</li>
                </ul>
                
                <p>You can now log in to access the system:</p>
                <a href="{settings.FRONTEND_URL}/login" class="button">Login to IMS</a>
                
                <p>If you have any questions, please contact your administrator.</p>
                
                <p>Best regards,<br>IMS Team</p>
            </div>
            <div class="footer">
                <p>© 2024 Inventory Management System. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Welcome to Inventory Management System!
    
    Hi {employee.first_name},
    
    Your account has been successfully created.
    
    Your Details:
    - Email: {employee.email}
    - Employee ID: {employee.employee_id}
    - Department: {employee.get_department_display()}
    
    You can now log in at: {settings.FRONTEND_URL}/login
    
    Best regards,
    IMS Team
    """
    
    return send_email_via_apps_script(
        employee.email,
        subject,
        html_content,
        text_content
    )


def send_password_reset_email(employee, reset_token):
    """Send password reset email"""
    reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token.token}"
    
    subject = "Reset Your Password - Inventory Management System"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
            .button {{ display: inline-block; padding: 12px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            .warning {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; border-radius: 5px; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Password Reset Request</h1>
            </div>
            <div class="content">
                <p>Hi {employee.first_name},</p>
                <p>We received a request to reset your password for your Inventory Management System account.</p>
                
                <p>Click the button below to reset your password:</p>
                <a href="{reset_url}" class="button">Reset Password</a>
                
                <div class="warning">
                    <strong>⚠️ Security Notice:</strong>
                    <p>This link will expire in 24 hours. If you didn't request this password reset, please ignore this email or contact your administrator.</p>
                </div>
                
                <p>Or copy and paste this URL into your browser:</p>
                <p style="word-break: break-all; color: #667eea;">{reset_url}</p>
                
                <p>Best regards,<br>IMS Team</p>
            </div>
            <div class="footer">
                <p>© 2024 Inventory Management System. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Password Reset Request
    
    Hi {employee.first_name},
    
    We received a request to reset your password.
    
    Click the link below to reset your password:
    {reset_url}
    
    This link will expire in 24 hours.
    
    If you didn't request this, please ignore this email.
    
    Best regards,
    IMS Team
    """
    
    return send_email_via_apps_script(
        employee.email,
        subject,
        html_content,
        text_content
    )


def send_password_changed_email(employee):
    """Send confirmation email after password change"""
    subject = "Password Changed - Inventory Management System"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
            .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
            .success {{ background: #d1fae5; border-left: 4px solid #10b981; padding: 15px; margin: 20px 0; border-radius: 5px; }}
            .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Password Changed Successfully</h1>
            </div>
            <div class="content">
                <p>Hi {employee.first_name},</p>
                
                <div class="success">
                    <p>✓ Your password has been successfully changed.</p>
                </div>
                
                <p>If you didn't make this change, please contact your administrator immediately.</p>
                
                <p>Best regards,<br>IMS Team</p>
            </div>
            <div class="footer">
                <p>© 2024 Inventory Management System. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Password Changed Successfully
    
    Hi {employee.first_name},
    
    Your password has been successfully changed.
    
    If you didn't make this change, please contact your administrator immediately.
    
    Best regards,
    IMS Team
    """
    
    return send_email_via_apps_script(
        employee.email,
        subject,
        html_content,
        text_content
    )