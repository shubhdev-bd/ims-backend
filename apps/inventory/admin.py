from django.contrib import admin
from .models import Device, Assignment, TicketRequest

@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ['device_id', 'name', 'device_type', 'status', 'condition']
    list_filter = ['device_type', 'status', 'condition']
    search_fields = ['device_id', 'name', 'brand', 'model']

@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['device', 'employee', 'assigned_date', 'status']
    list_filter = ['status', 'assigned_date']
    search_fields = ['device__device_id', 'employee__email']

@admin.register(TicketRequest)
class TicketRequestAdmin(admin.ModelAdmin):
    list_display = ['ticket_number', 'requested_by', 'ticket_type', 'priority', 'status']
    list_filter = ['ticket_type', 'priority', 'status']
    search_fields = ['ticket_number', 'subject']