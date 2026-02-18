"""
Inventory Views
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Count
from django.utils import timezone
from .models import Device, Assignment, TicketRequest
from apps.authentication.models import Employee
from .serializers import (
    DeviceSerializer,
    DeviceListSerializer,
    AssignmentSerializer,
    AssignmentListSerializer,
    TicketRequestSerializer,
    TicketRequestListSerializer,
    DashboardStatsSerializer,
)
from .permissions import IsAdminOrReadOnly, IsAdminOrManager


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
    """ViewSet for Assignment model"""
    
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
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filter by employee
        employee_id = self.request.query_params.get('employee')
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        
        # Filter by device
        device_id = self.request.query_params.get('device')
        if device_id:
            queryset = queryset.filter(device_id=device_id)
        
        # Show only user's assignments if not admin/manager
        if self.request.user.role not in ['admin', 'manager']:
            queryset = queryset.filter(employee=self.request.user)
        
        return queryset
    
    def perform_create(self, serializer):
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
    
    @action(detail=False, methods=['get'])
    def my_assignments(self, request):
        """Get current user's assignments"""
        assignments = self.queryset.filter(employee=request.user, status='active')
        serializer = AssignmentListSerializer(assignments, many=True)
        return Response(serializer.data)


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
        serializer.save(requested_by=self.request.user)
    
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
            device_assignments__status='active'
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