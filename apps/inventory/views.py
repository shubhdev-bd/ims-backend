"""
Inventory Views
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from django.utils import timezone
from django.conf import settings
from urllib3 import request
from .email_service import email_service
from .serializers import (
    DeviceSerializer,
    DeviceListSerializer,
    AssignmentSerializer,
    AssignmentListSerializer,
    TicketRequestSerializer,
    TicketRequestListSerializer,
    DeviceRequestSerializer,
    DeviceRequestListSerializer,
    DashboardStatsSerializer,
)
from .permissions import IsAdminOrReadOnly, IsAdminOrManager
from .models import Device, Assignment, TicketRequest, DeviceRequest
from apps.authentication.models import Employee

from django.shortcuts import render

def home(request):
    return render(request, 'index.html')


class DeviceViewSet(viewsets.ModelViewSet):
    """ViewSet for Device model"""
    
    queryset = Device.objects.all()
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['device_id', 'name', 'brand', 'model', 'serial_number']
    ordering_fields = ['created_at', 'name', 'status']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DeviceListSerializer
        return DeviceSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filter by device type
        device_type = self.request.query_params.get('device_type')
        if device_type:
            queryset = queryset.filter(device_type=device_type)
        
        # Filter by condition
        condition = self.request.query_params.get('condition')
        if condition:
            queryset = queryset.filter(condition=condition)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """Get all available devices"""
        devices = self.queryset.filter(status='available')
        serializer = DeviceListSerializer(devices, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_maintenance(self, request, pk=None):
        """Mark device as under maintenance"""
        device = self.get_object()
        device.status = 'maintenance'
        device.save()
        serializer = self.get_serializer(device)
        return Response({
            'message': 'Device marked as under maintenance',
            'device': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def mark_available(self, request, pk=None):
        """Mark device as available"""
        device = self.get_object()
        
        # Check if device has active assignments
        if device.assignments.filter(status='active').exists():
            return Response({
                'error': 'Cannot mark device as available. It has active assignments.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        device.status = 'available'
        device.save()
        serializer = self.get_serializer(device)
        return Response({
            'message': 'Device marked as available',
            'device': serializer.data
        })


class AssignmentViewSet(viewsets.ModelViewSet):
    queryset = Assignment.objects.all()
    permission_classes = [IsAuthenticated, IsAdminOrManager]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['device__device_id', 'device__name', 'employee__first_name', 'employee__last_name']
    ordering_fields = ['assigned_date', 'return_date']
    ordering = ['-assigned_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return AssignmentListSerializer
        return AssignmentSerializer

    def get_queryset(self):                          # ← indented inside class
        queryset = super().get_queryset()
        user = self.request.user

        if getattr(self, 'swagger_fake_view', False):
            return queryset.none()

        if not user.is_authenticated:
            return queryset.none()

        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        employee_id = self.request.query_params.get('employee')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)

        device_id = self.request.query_params.get('device')
        if device_id:
            queryset = queryset.filter(device_id=device_id)

        if getattr(user, 'role', None) not in ['admin', 'manager']:
            queryset = queryset.filter(employee=user)

        return queryset

    def perform_create(self, serializer):            # ← continues inside class
        serializer.save(assigned_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def return_device(self, request, pk=None):
        """Mark assignment as returned"""
        assignment = self.get_object()
        
        if assignment.status != 'active':
            return Response({
                'error': 'Only active assignments can be returned'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        assignment.status = 'returned'
        assignment.return_date = timezone.now()
        assignment.return_notes = request.data.get('return_notes', '')
        assignment.save()
        
        serializer = self.get_serializer(assignment)
        return Response({
            'message': 'Device returned successfully',
            'assignment': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def submit_consent(self, request, pk=None):
        """Submit consent form by user"""
        assignment = self.get_object()
        
        if assignment.employee != request.user:
            return Response({
                'error': 'You can only submit consent for your own assignments'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if assignment.status != 'approved':
            return Response({
                'error': 'Assignment must be approved before submitting consent'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        consent_data = request.data.get('consent_form_data', {})
        consent_images = request.data.get('consent_images', [])
        
        assignment.consent_form_data = consent_data
        assignment.consent_images = consent_images
        assignment.status = 'consent_pending'
        assignment.save()
        
        serializer = self.get_serializer(assignment)
        return Response({
            'message': 'Consent form submitted successfully',
            'assignment': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def approve_consent(self, request, pk=None):
        """Approve consent form by admin"""
        assignment = self.get_object()
        
        if request.user.role not in ['admin', 'manager']:
            return Response({
                'error': 'Only admins and managers can approve consent'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if assignment.status != 'consent_pending':
            return Response({
                'error': 'Consent is not pending approval'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        assignment.consent_approved = True
        assignment.consent_approved_at = timezone.now()
        assignment.consent_approved_by = request.user
        assignment.status = 'active'
        assignment.save()
        
        # Send email notification through Apps Script
        email_service.send_assignment_approved_email(assignment)

        serializer = self.get_serializer(assignment)
        return Response({
            'message': 'Consent approved successfully',
            'assignment': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def submit_return_form(self, request, pk=None):
        """Submit return form by user"""
        assignment = self.get_object()
        
        if assignment.employee != request.user:
            return Response({
                'error': 'You can only submit return form for your own assignments'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if assignment.status != 'active':
            return Response({
                'error': 'Assignment must be active to submit return form'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        return_data = request.data.get('return_form_data', {})
        return_images = request.data.get('return_images', [])
        
        assignment.return_form_data = return_data
        assignment.return_images = return_images
        assignment.status = 'returned'
        assignment.return_date = timezone.now()
        assignment.save()
        
        serializer = self.get_serializer(assignment)
        return Response({
            'message': 'Return form submitted successfully',
            'assignment': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def approve_return(self, request, pk=None):
        """Approve return by admin"""
        assignment = self.get_object()
        
        if request.user.role not in ['admin', 'manager']:
            return Response({
                'error': 'Only admins and managers can approve returns'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if assignment.status != 'returned':
            return Response({
                'error': 'Assignment must be returned to approve'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        assignment.return_approved = True
        assignment.return_approved_at = timezone.now()
        assignment.return_approved_by = request.user
        assignment.save()
        
        serializer = self.get_serializer(assignment)
        return Response({
            'message': 'Return approved successfully',
            'assignment': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def my_assignments(self, request):
        """Get current user's assignments"""
        assignments = Assignment.objects.filter(employee=request.user)
        
        # Optional status filter from query param
        status_param = request.query_params.get('status')
        if status_param:
            assignments = assignments.filter(status=status_param)
        
        serializer = AssignmentListSerializer(assignments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def grant_device(self, request, pk=None):
        """Grant device to user and send notification emails"""
        assignment = self.get_object()
        
        if request.user.role not in ['admin', 'manager']:
            return Response({
                'error': 'Only admins and managers can grant devices'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if assignment.status not in ['active', 'consent_pending']:
            return Response({
                'error': 'Assignment must be active or consent pending to grant'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        assignment.status = 'active'
        assignment.save()
        
        # Send grant email to all recipients
        from django.conf import settings
        
        recipients = {
            'employee': assignment.employee.email,
            'admin_recipients': settings.ADMIN_EMAIL_RECIPIENTS if hasattr(settings, 'ADMIN_EMAIL_RECIPIENTS') else []
        }
        
        # Build email content
        subject = f"Device Assignment Notification - {assignment.device.device_id}"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; }}
                .header {{ background-color: #2c3e50; color: white; padding: 20px; text-align: center; }}
                .content {{ background-color: white; padding: 20px; }}
                .device-info {{ background-color: #ecf0f1; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .footer {{ text-align: center; color: #7f8c8d; padding: 20px; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Device Assignment Notification</h1>
                </div>
                <div class="content">
                    <p>Dear {assignment.employee.full_name},</p>
                    
                    <p>Your device request has been approved and the following device has been assigned to you:</p>
                    
                    <div class="device-info">
                        <h3>Device Details</h3>
                        <p><strong>Device ID:</strong> {assignment.device.device_id}</p>
                        <p><strong>Device Type:</strong> {assignment.device.device_type.title()}</p>
                        <p><strong>Brand & Model:</strong> {assignment.device.brand} {assignment.device.model}</p>
                        <p><strong>Condition:</strong> {assignment.device.condition.title()}</p>
                        <p><strong>Assignment Date:</strong> {assignment.assigned_date.strftime('%d-%b-%Y %H:%M')}</p>
                        <p><strong>Expected Return Date:</strong> {assignment.expected_return_date.strftime('%d-%b-%Y') if assignment.expected_return_date else 'Not specified'}</p>
                    </div>
                    
                    <h3>Important Terms:</h3>
                    <ul>
                        <li>Device remains the property of {settings.COMPANY_NAME if hasattr(settings, 'COMPANY_NAME') else 'the organization'}</li>
                        <li>Device must be returned in good condition</li>
                        <li>Report any issues immediately to the IT department</li>
                        <li>Unauthorized modifications are not permitted</li>
                        <li>Device must not be shared with third parties</li>
                    </ul>
                    
                    <p>Please confirm receipt and device condition. Contact your admin if you have any questions.</p>
                    
                    <p>Best regards,<br/>
                    <strong>Inventory Management System</strong></p>
                </div>
                <div class="footer">
                    <p>This is an automated notification. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Device Assignment Notification
        
        Dear {assignment.employee.full_name},
        
        Your device request has been approved and the following device has been assigned to you:
        
        Device Details:
        - Device ID: {assignment.device.device_id}
        - Device Type: {assignment.device.device_type.title()}
        - Brand & Model: {assignment.device.brand} {assignment.device.model}
        - Assignment Date: {assignment.assigned_date.strftime('%d-%b-%Y %H:%M')}
        - Expected Return Date: {assignment.expected_return_date.strftime('%d-%b-%Y') if assignment.expected_return_date else 'Not specified'}
        
        Important Terms:
        - Device remains the property of the organization
        - Device must be returned in good condition
        - Report any issues immediately
        
        Best regards,
        Inventory Management System
        """
        
        # Send to employee
        email_service.send_generic_email(
            [recipients['employee']],
            subject,
            text_body,
            html_body=html_body
        )
        
        # Send to admin recipients
        admin_cc_recipients = recipients['admin_recipients']
        if admin_cc_recipients:
            admin_subject = f"Device Grant Notification - {assignment.employee.full_name} ({assignment.device.device_id})"
            admin_html = f"""
            <p>A device has been granted to the following employee:</p>
            <p><strong>Employee:</strong> {assignment.employee.full_name}</p>
            <p><strong>Employee ID:</strong> {assignment.employee.employee_id}</p>
            <p><strong>Email:</strong> {assignment.employee.email}</p>
            <p><strong>Device ID:</strong> {assignment.device.device_id}</p>
            <p><strong>Device:</strong> {assignment.device.brand} {assignment.device.model}</p>
            <p><strong>Grant Date:</strong> {timezone.now().strftime('%d-%b-%Y %H:%M')}</p>
            <p>Please keep this record for your reference.</p>
            """
            admin_text = f"Device {assignment.device.device_id} granted to {assignment.employee.full_name} ({assignment.employee.email})"
            
            email_service.send_generic_email(
                admin_cc_recipients,
                admin_subject,
                admin_text,
                html_body=admin_html
            )
        
        serializer = self.get_serializer(assignment)
        return Response({
            'message': 'Device granted successfully and notifications sent',
            'assignment': serializer.data,
            'emails_sent_to': [recipients['employee']] + admin_cc_recipients
        })


class TicketRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for TicketRequest model"""
    
    queryset = TicketRequest.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['ticket_number', 'subject', 'description']
    ordering_fields = ['created_at', 'priority', 'status']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return TicketRequestListSerializer
        return TicketRequestSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filter by ticket type
        ticket_type = self.request.query_params.get('ticket_type')
        if ticket_type:
            queryset = queryset.filter(ticket_type=ticket_type)
        
        # Filter by priority
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Show only user's tickets if not admin/manager
        if self.request.user.role not in ['admin', 'manager']:
            queryset = queryset.filter(
                Q(requested_by=self.request.user) | Q(assigned_to=self.request.user)
            )
        
        return queryset
    
    def perform_create(self, serializer):
        ticket = serializer.save(requested_by=self.request.user)
        email_service.send_ticket_created_email(ticket)

    @action(detail=True, methods=['post'])
    def assign(self, request, pk=None):
        """Assign ticket to an employee"""
        ticket = self.get_object()
        employee_id = request.data.get('assigned_to')
        
        if not employee_id:
            return Response({
                'error': 'Employee ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            employee = Employee.objects.get(id=employee_id)
            ticket.assigned_to = employee
            ticket.status = 'in_progress'
            ticket.save()
            
            email_service.send_ticket_assigned_email(ticket)
            
            serializer = self.get_serializer(ticket)
            return Response({
                'message': f'Ticket assigned to {employee.full_name}',
                'ticket': serializer.data
            })
        except Employee.DoesNotExist:
            return Response({
                'error': 'Employee not found'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark ticket as resolved"""
        ticket = self.get_object()
        
        resolution_notes = request.data.get('resolution_notes', '')
        if not resolution_notes:
            return Response({
                'error': 'Resolution notes are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        ticket.status = 'resolved'
        ticket.resolution_notes = resolution_notes
        ticket.resolved_at = timezone.now()
        ticket.save()
        
        email_service.send_ticket_resolved_email(ticket)
        
        serializer = self.get_serializer(ticket)
        return Response({
            'message': 'Ticket resolved successfully',
            'ticket': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def my_tickets(self, request):
        """Get current user's tickets"""
        tickets = self.queryset.filter(requested_by=request.user)
        serializer = TicketRequestListSerializer(tickets, many=True)
        return Response(serializer.data)


class DeviceRequestViewSet(viewsets.ModelViewSet):
    """ViewSet for DeviceRequest model"""
    
    queryset = DeviceRequest.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['device_type', 'brand', 'model', 'reason']
    ordering_fields = ['created_at', 'status']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        return DeviceRequestSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Show only user's requests if not admin/manager
        if self.request.user.role not in ['admin', 'manager']:
            queryset = queryset.filter(requested_by=self.request.user)
        
        return queryset
    
    def perform_create(self, serializer):
        device_request = serializer.save(requested_by=self.request.user)

        subject = "Device Request Submitted"
        html_body = f"""
        <p>Dear {self.request.user.full_name},</p>
        <p>Your device request has been submitted successfully.</p>
        <p><strong>Device Type:</strong> {device_request.device_type}</p>
        <p><strong>Brand:</strong> {device_request.brand or 'N/A'}</p>
        <p><strong>Model:</strong> {device_request.model or 'N/A'}</p>
        <p><strong>Reason:</strong> {device_request.reason}</p>
        <p>You will be notified once your request is reviewed.</p>
        <p>Best regards,<br/>Inventory Management System</p>
        """
        text_body = f"Device request submitted for {device_request.device_type}.\nReason: {device_request.reason}"

        email_service.send_generic_email(
            [self.request.user.email],
            subject,
            text_body,
            html_body=html_body,
        )

        admin_subject = f"New Device Request - {self.request.user.full_name}"
        admin_html = f"""
        <p>A new device request has been submitted.</p>
        <p><strong>Requested By:</strong> {self.request.user.full_name} ({self.request.user.email})</p>
        <p><strong>HRMS ID:</strong> {self.request.user.hrms_id or 'N/A'}</p>
        <p><strong>Device Type:</strong> {device_request.device_type}</p>
        <p><strong>Brand:</strong> {device_request.brand or 'N/A'}</p>
        <p><strong>Model:</strong> {device_request.model or 'N/A'}</p>
        <p><strong>Reason:</strong> {device_request.reason}</p>
        <p>Please review and approve/reject the request.</p>
        """
        admin_text = f"New device request submitted by {self.request.user.full_name} ({self.request.user.email}).\nDevice Type: {device_request.device_type}.\nReason: {device_request.reason}"

        admins = Employee.objects.filter(role='admin')
        admin_emails = [admin.email for admin in admins]
        if admin_emails:
            email_service.send_generic_email(
                admin_emails,
                admin_subject,
                admin_text,
                html_body=admin_html,
            )

    
    def _approve_device_request(self, request, device_request):
        if device_request.status != 'pending':
            return Response({
                'error': 'Request is not pending'
            }, status=status.HTTP_400_BAD_REQUEST)

        if request.user.role not in ['admin', 'manager']:
            return Response({
                'error': 'Only admins and managers can approve requests'
            }, status=status.HTTP_403_FORBIDDEN)

        device_request.status = 'consent_pending'
        device_request.approved_at = timezone.now()
        device_request.approved_by = request.user
        device_request.assignment = None  # Ensure no assignment is created
        device_request.save(update_fields=['status', 'approved_at', 'approved_by', 'assignment', 'updated_at'])

        # Optionally, send notification email here if needed

        serializer = self.get_serializer(device_request)
        return Response({
            'message': 'Device request approved, awaiting consent',
            'request': serializer.data
        })


    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a device request and set status to consent_pending."""
        return self._approve_device_request(request, self.get_object())

    # Grant endpoint is deprecated in new flow, but kept for backward compatibility
    @action(detail=True, methods=['post'])
    def grant(self, request, pk=None):
        return Response({
            'error': 'Grant flow is deprecated. Use approve to move to consent_pending.'
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject device request"""
        device_request = self.get_object()

        if device_request.status not in ['pending', 'consent_pending']:
            return Response({
                'error': 'Request is not pending or consent_pending'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Check if admin/manager
        if request.user.role not in ['admin', 'manager']:
            return Response({
                'error': 'Only admins and managers can reject requests'
            }, status=status.HTTP_403_FORBIDDEN)

        reason = request.data.get('reason', '')
        device_request.status = 'rejected'
        device_request.save(update_fields=['status', 'updated_at'])

        serializer = self.get_serializer(device_request)
        return Response({
            'message': 'Device request rejected',
            'request': serializer.data
        })



class DashboardViewSet(viewsets.ViewSet):
    """ViewSet for dashboard statistics"""
    
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get dashboard statistics"""
        
        # Device statistics
        total_devices = Device.objects.count()
        available_devices = Device.objects.filter(status='available').count()
        assigned_devices = Device.objects.filter(status='assigned').count()
        maintenance_devices = Device.objects.filter(status='maintenance').count()
        retired_devices = Device.objects.filter(status='retired').count()
        
        # Employee statistics
        total_employees = Employee.objects.filter(is_active=True).count()
        active_employees = Employee.objects.filter(
            is_active=True,
            assignments__status='active'
        ).distinct().count()
        
        # Assignment statistics
        total_assignments = Assignment.objects.count()
        active_assignments = Assignment.objects.filter(status='active').count()
        
        # Ticket statistics
        total_tickets = TicketRequest.objects.count()
        pending_tickets = TicketRequest.objects.filter(status='pending').count()
        in_progress_tickets = TicketRequest.objects.filter(status='in_progress').count()
        resolved_tickets = TicketRequest.objects.filter(status='resolved').count()
        
        # Device by type
        device_by_type = dict(
            Device.objects.values('device_type').annotate(
                count=Count('id')
            ).values_list('device_type', 'count')
        )
        
        # Recent data
        recent_assignments = Assignment.objects.all()[:5]
        recent_tickets = TicketRequest.objects.all()[:5]
        
        stats_data = {
            'total_devices': total_devices,
            'available_devices': available_devices,
            'assigned_devices': assigned_devices,
            'maintenance_devices': maintenance_devices,
            'retired_devices': retired_devices,
            'total_employees': total_employees,
            'active_employees': active_employees,
            'total_assignments': total_assignments,
            'active_assignments': active_assignments,
            'total_tickets': total_tickets,
            'pending_tickets': pending_tickets,
            'in_progress_tickets': in_progress_tickets,
            'resolved_tickets': resolved_tickets,
            'device_by_type': device_by_type,
            'recent_assignments': AssignmentListSerializer(recent_assignments, many=True).data,
            'recent_tickets': TicketRequestListSerializer(recent_tickets, many=True).data,
        }
        
        serializer = DashboardStatsSerializer(stats_data)
        return Response(serializer.data)


# views.py

import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Device


class UploadInventoryView(APIView):

    def post(self, request):
        file = request.FILES.get('file')

        if not file:
            return Response({"error": "No file uploaded"}, status=400)

        try:
            data = json.load(file)
        except Exception as e:
            return Response({"error": "Invalid JSON"}, status=400)

        inventory = data.get("inventory", {})
        created_devices = []
        
        def create_device(item, device_type, user):
            device_id = item.get("id")

            # Avoid duplicates
            if Device.objects.filter(device_id=device_id).exists():
                return None

            # Extract common fields
            brand = item.get("brand", "")
            model = item.get("model", "")

            # Remove known fields → rest goes to specifications
            excluded_keys = ["id", "brand", "model"]
            specifications = {k: v for k, v in item.items() if k not in excluded_keys}

            name = f"{brand} {model}".strip() or device_type

            device = Device.objects.create(
                device_id=device_id,
                name=name,
                device_type=device_type,
                brand=brand,
                model=model,
                specifications=specifications,
                status="available",
                created_by=user
            )

            return device
        

        # def create_device(item, device_type):
        #     device_id = item.get("id")

        #     # Avoid duplicates
        #     if Device.objects.filter(device_id=device_id).exists():
        #         return None

        #     # Extract common fields
        #     brand = item.get("brand", "")
        #     model = item.get("model", "")

        #     quantity = item.get("quantity", 1)

        #     # Remove known fields → rest goes to specs
        #     excluded_keys = ["id", "brand", "model", "quantity"]
        #     specs = {k: v for k, v in item.items() if k not in excluded_keys}

        #     description = f"{brand} {model} {device_type}".strip()

        #     device = Device.objects.create(
        #         device_id=device_id,
        #         device_type=device_type,
        #         brand=brand,
        #         model=model,
        #         specs=specs,
        #         description=description,
        #         quantity=quantity
        #     )

        #     return device

        # 🔥 Mapping JSON keys → model types
        mapping = {
            "laptops": "laptop",
            "mouse": "mouse",
            "keyboards": "keyboard",
            "sim_cards": "sim",
            "pc_setups": "pc",
            "headphones": "headphone"
        }

        for key, device_type in mapping.items():
            items = inventory.get(key, [])
            for item in items:
                device = create_device(item, device_type, request.user)
                if device:
                    created_devices.append(device.device_id)

        return Response({
            "message": "Inventory uploaded successfully",
            "created_devices": created_devices
        }, status=status.HTTP_201_CREATED)
