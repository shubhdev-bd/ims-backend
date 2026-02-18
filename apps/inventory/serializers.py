"""
Inventory Serializers
"""
from rest_framework import serializers
from apps.authentication.serializers import EmployeeSerializer
from .models import Device, Assignment, TicketRequest


class DeviceSerializer(serializers.ModelSerializer):
    """Serializer for Device model"""
    
    created_by_name = serializers.SerializerMethodField()
    current_assignment = serializers.SerializerMethodField()
    
    class Meta:
        model = Device
        fields = [
            'id', 'device_id', 'name', 'device_type', 'brand', 'model',
            'serial_number', 'status', 'condition', 'specifications',
            'purchase_date', 'purchase_price', 'warranty_expiry',
            'location', 'notes', 'image', 'created_at', 'updated_at',
            'created_by', 'created_by_name', 'current_assignment'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by']
    
    def get_created_by_name(self, obj):
        if obj.created_by:
            return obj.created_by.full_name
        return None
    
    def get_current_assignment(self, obj):
        assignment = obj.assignments.filter(status='active').first()
        if assignment:
            return {
                'id': str(assignment.id),
                'employee': assignment.employee.full_name,
                'employee_id': assignment.employee.employee_id,
                'assigned_date': assignment.assigned_date
            }
        return None


class DeviceListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for device list"""
    
    class Meta:
        model = Device
        fields = [
            'id', 'device_id', 'name', 'device_type', 'brand',
            'model', 'status', 'condition', 'location'
        ]


class AssignmentSerializer(serializers.ModelSerializer):
    """Serializer for Assignment model"""
    
    device_details = DeviceListSerializer(source='device', read_only=True)
    employee_details = EmployeeSerializer(source='employee', read_only=True)
    assigned_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'device', 'device_details', 'employee', 'employee_details',
            'assigned_date', 'return_date', 'expected_return_date',
            'status', 'assignment_notes', 'return_notes',
            'assigned_by', 'assigned_by_name'
        ]
        read_only_fields = ['id', 'assigned_date', 'assigned_by']
    
    def get_assigned_by_name(self, obj):
        if obj.assigned_by:
            return obj.assigned_by.full_name
        return None
    
    def validate(self, attrs):
        """Validate assignment data"""
        device = attrs.get('device')
        status = attrs.get('status', 'active')
        
        # Check if device is available for new assignments
        if self.instance is None and status == 'active':
            if device.status == 'assigned':
                active_assignment = device.assignments.filter(status='active').first()
                if active_assignment:
                    raise serializers.ValidationError(
                        f"Device is already assigned to {active_assignment.employee.full_name}"
                    )
            elif device.status not in ['available', 'assigned']:
                raise serializers.ValidationError(
                    f"Device is not available for assignment (Status: {device.get_status_display()})"
                )
        
        return attrs


class AssignmentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for assignment list"""
    
    device_name = serializers.CharField(source='device.name', read_only=True)
    device_id = serializers.CharField(source='device.device_id', read_only=True)
    employee_name = serializers.CharField(source='employee.full_name', read_only=True)
    employee_email = serializers.EmailField(source='employee.email', read_only=True)
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'device', 'device_name', 'device_id',
            'employee', 'employee_name', 'employee_email',
            'assigned_date', 'status'
        ]


class TicketRequestSerializer(serializers.ModelSerializer):
    """Serializer for TicketRequest model"""
    
    requested_by_details = EmployeeSerializer(source='requested_by', read_only=True)
    device_details = DeviceListSerializer(source='device', read_only=True)
    assigned_to_details = EmployeeSerializer(source='assigned_to', read_only=True)
    
    class Meta:
        model = TicketRequest
        fields = [
            'id', 'ticket_number', 'requested_by', 'requested_by_details',
            'ticket_type', 'priority', 'status', 'device', 'device_details',
            'subject', 'description', 'assigned_to', 'assigned_to_details',
            'resolution_notes', 'resolved_at', 'attachment',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'ticket_number', 'requested_by', 'created_at', 'updated_at']


class TicketRequestListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for ticket list"""
    
    requested_by_name = serializers.CharField(source='requested_by.full_name', read_only=True)
    device_name = serializers.CharField(source='device.name', read_only=True)
    
    class Meta:
        model = TicketRequest
        fields = [
            'id', 'ticket_number', 'requested_by', 'requested_by_name',
            'ticket_type', 'priority', 'status', 'device', 'device_name',
            'subject', 'created_at'
        ]


class DashboardStatsSerializer(serializers.Serializer):
    """Serializer for dashboard statistics"""
    
    total_devices = serializers.IntegerField()
    available_devices = serializers.IntegerField()
    assigned_devices = serializers.IntegerField()
    maintenance_devices = serializers.IntegerField()
    retired_devices = serializers.IntegerField()
    
    total_employees = serializers.IntegerField()
    active_employees = serializers.IntegerField()
    
    total_assignments = serializers.IntegerField()
    active_assignments = serializers.IntegerField()
    
    total_tickets = serializers.IntegerField()
    pending_tickets = serializers.IntegerField()
    in_progress_tickets = serializers.IntegerField()
    resolved_tickets = serializers.IntegerField()
    
    device_by_type = serializers.DictField()
    recent_assignments = AssignmentListSerializer(many=True)
    recent_tickets = TicketRequestListSerializer(many=True)