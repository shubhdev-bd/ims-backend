"""
Authentication Serializers
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.utils import timezone
from .models import Employee


class EmployeeSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = Employee
        fields = [
            'id',
            'email',
            'first_name',
            'last_name',
            'full_name',
            'employee_id',
            'hrms_id',
            'role',
            'department',
            'phone_number',
            'is_active',
            'date_joined',
            'profile_picture_url',
        ]
        read_only_fields = [
            'id',
            'employee_id',
            'date_joined',
        ]


class SignupSerializer(serializers.ModelSerializer):
    """Serializer for employee signup"""
    
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = Employee
        fields = [
            'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'hrms_id', 'department', 'phone_number'
        ]
    
    def validate(self, attrs):
        """Validate passwords match"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs
    
    def create(self, validated_data):
        """Create new employee"""
        validated_data.pop('password_confirm')
        
        employee = Employee.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            hrms_id=validated_data.get('hrms_id'),
            department=validated_data.get('department', ''),
            phone_number=validated_data.get('phone_number', ''),
        )
        return employee


class LoginSerializer(serializers.Serializer):
    """Serializer for employee login"""
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validate credentials"""
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            # Authenticate user
            user = authenticate(
                request=self.context.get('request'),
                username=email,
                password=password
            )
            
            if not user:
                raise serializers.ValidationError(
                    'Unable to log in with provided credentials.',
                    code='authorization'
                )
            
            if not user.is_active:
                raise serializers.ValidationError(
                    'User account is disabled.',
                    code='authorization'
                )
            
            attrs['user'] = user
            return attrs
        else:
            raise serializers.ValidationError(
                'Must include "email" and "password".',
                code='authorization'
            )


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for password reset request"""
    
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Validate that email exists"""
        try:
            Employee.objects.get(email=value, is_active=True)
        except Employee.DoesNotExist:
            # Don't reveal if email exists or not for security
            pass
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for password reset confirmation"""
    
    token = serializers.CharField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validate passwords match"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                "password": "Password fields didn't match."
            })
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing password"""
    
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validate passwords match"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                "new_password": "Password fields didn't match."
            })
        return attrs
    
class EmployeeCreateUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Employee
        fields = [
            'email',
            'first_name',
            'last_name',
            'role',
            'department',
            'phone_number',
            'is_active',
            'password',
        ]

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = Employee.objects.create_user(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class VerifyEmailOTPSerializer(serializers.Serializer):
    """Serializer for verifying email OTP"""
    
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, max_length=6)
    
    def validate_otp(self, value):
        """Validate OTP format"""
        if not value.isdigit():
            raise serializers.ValidationError("OTP must be numeric")
        if len(value) != 6:
            raise serializers.ValidationError("OTP must be 6 digits")
        return value
    
    def validate(self, attrs):
        """Validate OTP against employee"""
        email = attrs.get('email')
        otp = attrs.get('otp')
        
        try:
            employee = Employee.objects.get(email=email, is_active=True)
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Invalid email address")
        
        try:
            from .models import EmailOTP
            email_otp = EmailOTP.objects.get(employee=employee)
        except EmailOTP.DoesNotExist:
            raise serializers.ValidationError("No OTP found for this email")
        
        # Check if OTP is valid
        if not email_otp.is_valid():
            raise serializers.ValidationError("OTP has expired or already used")
        
        # Check OTP
        if email_otp.otp != otp:
            email_otp.attempt_count += 1
            email_otp.save()
            if email_otp.attempt_count >= 5:
                email_otp.delete()
            raise serializers.ValidationError("Invalid OTP")
        
        # Mark as verified
        email_otp.is_verified = True
        email_otp.save()
        
        # Mark employee email as verified
        employee.email_verified = True
        employee.email_verified_at = timezone.now()
        employee.save()
        
        attrs['employee'] = employee
        return attrs


class ChangePasswordAfterOTPSerializer(serializers.Serializer):
    """Serializer for changing password after OTP verification"""
    
    email = serializers.EmailField(required=True)
    otp = serializers.CharField(required=True, max_length=6)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate(self, attrs):
        """Validate passwords match and OTP"""
        email = attrs.get('email')
        otp = attrs.get('otp')
        new_password = attrs.get('new_password')
        new_password_confirm = attrs.get('new_password_confirm')
        
        # Validate passwords match
        if new_password != new_password_confirm:
            raise serializers.ValidationError({
                "new_password": "Password fields didn't match."
            })
        
        # Validate OTP
        try:
            employee = Employee.objects.get(email=email, is_active=True)
        except Employee.DoesNotExist:
            raise serializers.ValidationError("Invalid email address")
        
        try:
            from .models import EmailOTP
            email_otp = EmailOTP.objects.get(employee=employee)
        except EmailOTP.DoesNotExist:
            raise serializers.ValidationError("No OTP found for this email")
        
        if not email_otp.is_valid():
            raise serializers.ValidationError("OTP has expired or already used")
        
        if email_otp.otp != otp:
            email_otp.attempt_count += 1
            email_otp.save()
            raise serializers.ValidationError("Invalid OTP")
        
        attrs['employee'] = employee
        attrs['email_otp'] = email_otp
        return attrs
    
    def save(self):
        """Save new password"""
        employee = self.validated_data['employee']
        email_otp = self.validated_data['email_otp']
        new_password = self.validated_data['new_password']
        
        employee.set_password(new_password)
        employee.email_verified = True
        employee.email_verified_at = timezone.now()
        employee.save()
        
        email_otp.is_verified = True
        email_otp.save()
        
        from .utils import send_password_changed_email
        send_password_changed_email(employee)
        
        return employee
