"""
Authentication URLs
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    EmployeeDetailView,
    EmployeeListCreateView,
    SignupView,
    LoginView,
    LogoutView,
    CurrentEmployeeView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    ChangePasswordView,
    VerifyTokenView,
)

urlpatterns = [
    # Authentication
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Profile
    path('me/', CurrentEmployeeView.as_view(), name='current_employee'),
    
    # Password Management
    path('password/change/', ChangePasswordView.as_view(), name='change_password'),
    path('password/reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password/reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password/reset/verify/', VerifyTokenView.as_view(), name='verify_reset_token'),

    path('employees/', EmployeeListCreateView.as_view()),
    path('employees/<uuid:pk>/', EmployeeDetailView.as_view()),
]