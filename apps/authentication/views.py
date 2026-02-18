"""
Authentication Views
"""
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import logout
from .models import Employee, PasswordResetToken
from .serializers import (
    EmployeeSerializer,
    SignupSerializer,
    LoginSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    ChangePasswordSerializer
)
from .permissions import IsAdmin
from .serializers import EmployeeSerializer, EmployeeCreateUpdateSerializer

from .utils import (
    create_password_reset_token,
    send_welcome_email,
    send_password_reset_email,
    send_password_changed_email
)


class SignupView(generics.CreateAPIView):
    """Employee signup endpoint"""
    
    permission_classes = [AllowAny]
    serializer_class = SignupSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create employee
        employee = serializer.save()
        
        # Send welcome email
        send_welcome_email(employee)
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(employee)
        
        # Return employee data with tokens
        employee_serializer = EmployeeSerializer(employee)
        
        return Response({
            'message': 'Account created successfully',
            'employee': employee_serializer.data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    """Employee login endpoint"""
    
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    
    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        employee = serializer.validated_data['user']
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(employee)
        
        # Update last login
        employee.save(update_fields=['last_login'])
        
        # Return employee data with tokens
        employee_serializer = EmployeeSerializer(employee)
        
        return Response({
            'message': 'Login successful',
            'employee': employee_serializer.data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    """Employee logout endpoint"""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            logout(request)
            
            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Invalid token'
            }, status=status.HTTP_400_BAD_REQUEST)


class CurrentEmployeeView(generics.RetrieveUpdateAPIView):
    """Get or update current employee profile"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = EmployeeSerializer
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        
        # Don't allow updating certain fields
        non_updatable = ['email', 'employee_id', 'role', 'is_active', 'is_staff', 'date_joined']
        for field in non_updatable:
            if field in request.data:
                request.data.pop(field)
        
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response({
            'message': 'Profile updated successfully',
            'employee': serializer.data
        })


class PasswordResetRequestView(APIView):
    """Request password reset"""
    
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        try:
            employee = Employee.objects.get(email=email, is_active=True)
            
            # Create reset token
            reset_token = create_password_reset_token(employee)
            
            # Send reset email
            send_password_reset_email(employee, reset_token)
            
        except Employee.DoesNotExist:
            # Don't reveal if email exists
            pass
        
        # Always return success for security
        return Response({
            'message': 'If your email is registered, you will receive a password reset link shortly.'
        }, status=status.HTTP_200_OK)


class PasswordResetConfirmView(APIView):
    """Confirm password reset with token"""
    
    permission_classes = [AllowAny]
    serializer_class = PasswordResetConfirmSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        token = serializer.validated_data['token']
        new_password = serializer.validated_data['password']
        
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
            
            if not reset_token.is_valid():
                return Response({
                    'error': 'Invalid or expired token'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Update password
            employee = reset_token.employee
            employee.set_password(new_password)
            employee.save()
            
            # Mark token as used
            reset_token.is_used = True
            reset_token.save()
            
            # Send confirmation email
            send_password_changed_email(employee)
            
            return Response({
                'message': 'Password has been reset successfully'
            }, status=status.HTTP_200_OK)
            
        except PasswordResetToken.DoesNotExist:
            return Response({
                'error': 'Invalid token'
            }, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """Change password for authenticated user"""
    
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        employee = request.user
        
        # Check old password
        if not employee.check_password(serializer.validated_data['old_password']):
            return Response({
                'error': 'Old password is incorrect'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Set new password
        employee.set_password(serializer.validated_data['new_password'])
        employee.save()
        
        # Send confirmation email
        send_password_changed_email(employee)
        
        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)


class VerifyTokenView(APIView):
    """Verify if reset token is valid"""
    
    permission_classes = [AllowAny]
    
    def get(self, request):
        token = request.query_params.get('token')
        
        if not token:
            return Response({
                'valid': False,
                'error': 'Token is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            reset_token = PasswordResetToken.objects.get(token=token)
            
            if reset_token.is_valid():
                return Response({
                    'valid': True,
                    'email': reset_token.employee.email
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'valid': False,
                    'error': 'Token has expired or already been used'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except PasswordResetToken.DoesNotExist:
            return Response({
                'valid': False,
                'error': 'Invalid token'
            }, status=status.HTTP_400_BAD_REQUEST)
        
from rest_framework import generics, permissions
from .models import Employee
from .serializers import EmployeeSerializer

class EmployeeListCreateView(generics.ListCreateAPIView):
    queryset = Employee.objects.filter(is_active=True)
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAdminUser]


class EmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [permissions.IsAdminUser]

    def perform_destroy(self, instance):
        # Soft delete
        instance.is_active = False
        instance.save()

class EmployeeListCreateView(generics.ListCreateAPIView):
    queryset = Employee.objects.filter(is_active=True)
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return EmployeeCreateUpdateSerializer
        return EmployeeSerializer

class EmployeeDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Employee.objects.all()
    permission_classes = [IsAdmin]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return EmployeeCreateUpdateSerializer
        return EmployeeSerializer

    def perform_destroy(self, instance):
        instance.is_active = False
        instance.save()
