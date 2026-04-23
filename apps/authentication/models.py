"""
Authentication Models
"""
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
import uuid


class EmployeeManager(BaseUserManager):
    """Custom manager for Employee model"""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user"""
        if not email:
            raise ValueError('Email address is required')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser"""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'admin')
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')
        
        return self.create_user(email, password, **extra_fields)


class Employee(AbstractBaseUser, PermissionsMixin):
    """Custom Employee model"""
    
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('manager', 'Manager'),
        ('employee', 'Employee'),
    ]
    
    DEPARTMENT_CHOICES = [
        ('IT', 'Information Technology'),
        ('HR', 'Human Resources'),
        ('Finance', 'Finance'),
        ('Operations', 'Operations'),
        ('Sales', 'Sales'),
        ('Marketing', 'Marketing'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(max_length=150, unique=True, db_index=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    employee_id = models.CharField(max_length=20, unique=True, blank=True, null=True)
    hrms_id = models.CharField(max_length=50, unique=True, blank=True, null=True)
    
    # Role and Department
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, blank=True)
    
    # Contact Information
    phone_number = models.CharField(max_length=15, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    
    # Timestamps
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    email_verified_at = models.DateTimeField(null=True, blank=True)
    
    # Profile
    profile_picture_url = models.URLField(max_length=500, null=True, blank=True, help_text="URL to profile picture from Vercel Blob or similar")
    
    objects = EmployeeManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        db_table = 'employees'
        ordering = ['-date_joined']
        verbose_name = 'Employee'
        verbose_name_plural = 'Employees'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"

    def _build_username_base(self):
        """Build a readable username from the employee's name."""
        name_parts = [
            (self.first_name or "").strip(),
            (self.last_name or "").strip(),
        ]
        full_name = " ".join(part for part in name_parts if part)
        if full_name:
            return slugify(full_name).replace("-", ".")
        if self.email:
            return self.email.split("@", 1)[0].lower()
        if self.employee_id:
            return self.employee_id.lower()
        return f"user.{str(self.id)[:8]}"

    def generate_unique_username(self):
        """Generate a unique username for login."""
        base_username = self._build_username_base().strip(".") or "user"
        base_username = base_username[:140]
        candidate = base_username
        suffix = 1

        while Employee.objects.exclude(pk=self.pk).filter(username__iexact=candidate).exists():
            suffix_text = str(suffix)
            candidate = f"{base_username[:150 - len(suffix_text)]}{suffix_text}"
            suffix += 1

        return candidate.lower()
    
    @property
    def full_name(self):
        """Return full name of employee"""
        return f"{self.first_name} {self.last_name}"
    
    def save(self, *args, **kwargs):
        """Override save to generate employee_id if not exists"""
        if not self.employee_id:
            # Generate employee ID like EMP001, EMP002, etc.
            last_employee = Employee.objects.all().order_by('date_joined').last()
            if last_employee and last_employee.employee_id:
                last_id = int(last_employee.employee_id[3:])
                self.employee_id = f"EMP{str(last_id + 1).zfill(3)}"
            else:
                self.employee_id = "EMP001"

        if self.username:
            self.username = self.username.strip().lower()
        else:
            self.username = self.generate_unique_username()
        super().save(*args, **kwargs)


class PasswordResetToken(models.Model):
    """Model to store password reset tokens"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='reset_tokens')
    token = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'password_reset_tokens'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Reset token for {self.employee.email}"
    
    def is_valid(self):
        """Check if token is still valid"""
        return not self.is_used and timezone.now() < self.expires_at


class EmailOTP(models.Model):
    """Model to store OTP for email verification"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='email_otp')
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_verified = models.BooleanField(default=False)
    attempt_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'email_otps'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"OTP for {self.employee.email}"
    
    def is_valid(self):
        """Check if OTP is still valid"""
        return not self.is_verified and timezone.now() < self.expires_at and self.attempt_count < 5
