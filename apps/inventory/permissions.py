"""
Inventory Permissions
"""
from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admins to edit objects.
    Other users have read-only access.
    """
    
    def has_permission(self, request, view):
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for admin users
        return request.user.role == 'admin'


class IsAdminOrManager(permissions.BasePermission):
    """
    Custom permission to allow admins and managers to perform actions.
    Employees can only view their own data.
    """
    
    def has_permission(self, request, view):
        # Admin and manager have full access
        if request.user.role in ['admin', 'manager']:
            return True
        
        # Employees can only read
        return request.method in permissions.SAFE_METHODS
    
    def has_object_permission(self, request, view, obj):
        # Admin and manager have full access
        if request.user.role in ['admin', 'manager']:
            return True
        
        # Employees can only view their own assignments
        if hasattr(obj, 'employee'):
            return obj.employee == request.user
        
        return False


class IsOwnerOrAdminOrManager(permissions.BasePermission):
    """
    Custom permission to allow owners, admins, and managers to edit.
    """
    
    def has_object_permission(self, request, view, obj):
        # Admin and manager have full access
        if request.user.role in ['admin', 'manager']:
            return True
        
        # Owner can edit their own object
        if hasattr(obj, 'requested_by'):
            return obj.requested_by == request.user
        
        return False