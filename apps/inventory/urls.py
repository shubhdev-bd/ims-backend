"""
Inventory URLs
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DeviceViewSet,
    AssignmentViewSet,
    TicketRequestViewSet,
    DeviceRequestViewSet,
    DashboardViewSet,
)

router = DefaultRouter()
router.register(r'devices', DeviceViewSet, basename='device')
router.register(r'assignments', AssignmentViewSet, basename='assignment')
router.register(r'tickets', TicketRequestViewSet, basename='ticket')
router.register(r'device-requests', DeviceRequestViewSet, basename='device-request')
router.register(r'dashboard', DashboardViewSet, basename='dashboard')

urlpatterns = [
    path('', include(router.urls)),
]