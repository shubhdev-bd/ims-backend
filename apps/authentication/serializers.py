"""
Authentication Serializers
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from .models import Employee


class EmployeeSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()
    assigned_devices_count = serializers.SerializerMethodField()

    ACTIVE_ASSIGNMENT_STATUSES = {'active', 'approved'}
    ACTIVE_INVENTORY_STATUSES = {'assigned', 'pending_claim', 'claimed'}

    def get_assigned_devices_count(self, obj):
        prefetched_assignments = getattr(obj, '_prefetched_objects_cache', {}).get('assignments')
        assignment_count = None
        if prefetched_assignments is not None:
            assignment_count = sum(
                1 for assignment in prefetched_assignments
                if assignment.status in self.ACTIVE_ASSIGNMENT_STATUSES
            )
        else:
            assignment_count = obj.assignments.filter(
                status__in=self.ACTIVE_ASSIGNMENT_STATUSES,
            ).count()

        prefetched_inventory_assets = getattr(
            obj,
            '_prefetched_objects_cache',
            {},
        ).get('inventory_assets')
        if prefetched_inventory_assets is not None:
            inventory_count = sum(
                1 for asset in prefetched_inventory_assets
                if asset.status in self.ACTIVE_INVENTORY_STATUSES
            )
        else:
            inventory_count = obj.inventory_assets.filter(
                status__in=self.ACTIVE_INVENTORY_STATUSES,
            ).count()

        return assignment_count + inventory_count

    class Meta:
        model = Employee
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'full_name',
            'employee_id',
            'hrms_id',
            'role',
            'department',
            'phone_number',
            'is_active',
            'email_verified',
            'email_verified_at',
            'date_joined',
            'profile_picture_url',
            'assigned_devices_count',
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

    login = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    admin_only = serializers.BooleanField(required=False, default=False)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )

    def validate(self, attrs):
        """Validate credentials"""
        login_identifier = attrs.get('login') or attrs.get('email')
        password = attrs.get('password')
        admin_only = attrs.get('admin_only', False)

        if not login_identifier or not password:
            raise serializers.ValidationError(
                'Must include "login" and "password".',
                code='authorization'
            )

        login_identifier = login_identifier.strip()

        if '@' in login_identifier:
            user = Employee.objects.filter(email__iexact=login_identifier).first()
        else:
            user = Employee.objects.filter(username__iexact=login_identifier).first()

        if not user or not user.check_password(password):
            raise serializers.ValidationError(
                'Unable to log in with provided credentials.',
                code='authorization'
            )

        if not user.is_active:
            raise serializers.ValidationError(
                'User account is disabled.',
                code='authorization'
            )

        if admin_only and user.role != 'admin':
            raise serializers.ValidationError(
                'This login page is for admin accounts only.',
                code='authorization'
            )

        attrs['user'] = user
        attrs['login'] = login_identifier
        return attrs


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
            'username',
            'first_name',
            'last_name',
            'role',
            'department',
            'phone_number',
            'is_active',
            'password',
        ]

    def validate_username(self, value):
        if not value:
            return value
        return value.strip().lower()

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
