"""
Inventory Models
"""
from django.db import models
from django.conf import settings
import uuid


class Device(models.Model):
    """Model for devices in inventory"""
    
    DEVICE_TYPE_CHOICES = [
        ('laptop', 'Laptop'),
        ('desktop', 'Desktop'),
        ('monitor', 'Monitor'),
        ('keyboard', 'Keyboard'),
        ('mouse', 'Mouse'),
        ('headset', 'Headset'),
        ('phone', 'Phone'),
        ('tablet', 'Tablet'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('assigned', 'Assigned'),
        ('maintenance', 'Under Maintenance'),
        ('retired', 'Retired'),
    ]
    
    CONDITION_CHOICES = [
        ('new', 'New'),
        ('excellent', 'Excellent'),
        ('good', 'Good'),
        ('fair', 'Fair'),
        ('poor', 'Poor'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    device_type = models.CharField(max_length=20, choices=DEVICE_TYPE_CHOICES)
    brand = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    serial_number = models.CharField(max_length=100, unique=True, blank=True, null=True)
    
    # Status and Condition
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES, default='good')
    
    # Specifications
    specifications = models.JSONField(default=dict, blank=True)
    
    # Purchase Information
    purchase_date = models.DateField(null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    warranty_expiry = models.DateField(null=True, blank=True)
    
    # Location
    location = models.CharField(max_length=200, blank=True)
    
    # Additional Information
    notes = models.TextField(blank=True)
    image = models.ImageField(upload_to='devices/', null=True, blank=True)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='devices_created'
    )
    
    class Meta:
        db_table = 'devices'
        ordering = ['-created_at']
        verbose_name = 'Device'
        verbose_name_plural = 'Devices'
    
    def __str__(self):
        return f"{self.device_id} - {self.name}"


class Assignment(models.Model):
    """Model for device assignments to employees"""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('returned', 'Returned'),
        ('lost', 'Lost'),
        ('damaged', 'Damaged'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='assignments')
    employee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='device_assignments'
    )
    
    # Assignment Details
    assigned_date = models.DateTimeField(auto_now_add=True)
    return_date = models.DateTimeField(null=True, blank=True)
    expected_return_date = models.DateField(null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    
    # Notes
    assignment_notes = models.TextField(blank=True)
    return_notes = models.TextField(blank=True)
    
    # Assigned by
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assignments_created'
    )
    
    class Meta:
        db_table = 'assignments'
        ordering = ['-assigned_date']
        verbose_name = 'Assignment'
        verbose_name_plural = 'Assignments'
    
    def __str__(self):
        return f"{self.device.device_id} assigned to {self.employee.full_name}"
    
    def save(self, *args, **kwargs):
        """Update device status when assignment is created or updated"""
        is_new = self.pk is None
        
        super().save(*args, **kwargs)
        
        # Update device status based on assignment status
        if self.status == 'active':
            self.device.status = 'assigned'
        elif self.status == 'returned':
            self.device.status = 'available'
        elif self.status in ['lost', 'damaged']:
            self.device.status = 'maintenance'
        
        self.device.save(update_fields=['status'])


class TicketRequest(models.Model):
    """Model for support/maintenance ticket requests"""
    
    TICKET_TYPE_CHOICES = [
        ('repair', 'Repair Request'),
        ('replacement', 'Replacement Request'),
        ('new_device', 'New Device Request'),
        ('issue', 'Issue Report'),
        ('return', 'Return Request'),
        ('other', 'Other'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('rejected', 'Rejected'),
        ('closed', 'Closed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    ticket_number = models.CharField(max_length=20, unique=True, editable=False)
    
    # Requester
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tickets_created'
    )
    
    # Ticket Details
    ticket_type = models.CharField(max_length=20, choices=TICKET_TYPE_CHOICES)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Related Device (optional)
    device = models.ForeignKey(
        Device,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets'
    )
    
    # Description
    subject = models.CharField(max_length=200)
    description = models.TextField()
    
    # Assignment
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets_assigned'
    )
    
    # Resolution
    resolution_notes = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    
    # Attachments
    attachment = models.FileField(upload_to='tickets/', null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'ticket_requests'
        ordering = ['-created_at']
        verbose_name = 'Ticket Request'
        verbose_name_plural = 'Ticket Requests'
    
    def __str__(self):
        return f"{self.ticket_number} - {self.subject}"
    
    def save(self, *args, **kwargs):
        """Generate ticket number if not exists"""
        if not self.ticket_number:
            # Generate ticket number like TKT001, TKT002, etc.
            last_ticket = TicketRequest.objects.all().order_by('created_at').last()
            if last_ticket and last_ticket.ticket_number:
                last_num = int(last_ticket.ticket_number[3:])
                self.ticket_number = f"TKT{str(last_num + 1).zfill(3)}"
            else:
                self.ticket_number = "TKT001"
        
        super().save(*args, **kwargs)


class DashboardStats(models.Model):
    """Model to cache dashboard statistics (optional optimization)"""
    
    total_devices = models.IntegerField(default=0)
    available_devices = models.IntegerField(default=0)
    assigned_devices = models.IntegerField(default=0)
    maintenance_devices = models.IntegerField(default=0)
    
    total_employees = models.IntegerField(default=0)
    active_assignments = models.IntegerField(default=0)
    
    pending_tickets = models.IntegerField(default=0)
    resolved_tickets = models.IntegerField(default=0)
    
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'dashboard_stats'
        verbose_name = 'Dashboard Statistics'
        verbose_name_plural = 'Dashboard Statistics'