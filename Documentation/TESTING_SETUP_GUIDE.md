# IMS Backend Setup & Testing Guide

## Quick Start - Run All Phases

```bash
# 1. Navigate to backend directory
cd ims-backendd

# 2. Run migrations
python manage.py makemigrations
python manage.py migrate

# 3. Create test users (Phase 1)
python manage.py create_test_users

# 4. Load devices (Phase 2)
python manage.py load_devices

# 5. Start server
python manage.py runserver
```

---

## Phase 1 ✅ - Test Users Creation

### Command
```bash
python manage.py create_test_users
```

### Options
```bash
# Delete existing test users and recreate them
python manage.py create_test_users --delete
```

### Test Users Created
| Name | Email | Password | Department | Role |
|------|-------|----------|-----------|------|
| Arun Kumar Gautam | arun.gautam@believersdestination.com | TestPass@123 | IT | Employee |
| Vikas Chauhan | vikas.chauhan@believersdestination.com | TestPass@123 | IT | Employee |
| Vamika Singh | vamika@believersdestination.com | TestPass@123 | HR | Employee |
| Shubh Saxena | shubh.saxena@believersdestination.com | TestPass@123 | IT | Employee |
| Nikita Sharma | nikita@believersdestination.com | TestPass@123 | Operations | Employee |

### Expected Output
```
============================================================
Creating test users...
✓ Created: Arun Kumar Gautam (arun.gautam@believersdestination.com) | Employee ID: EMP001
✓ Created: Vikas Chauhan (vikas.chauhan@believersdestination.com) | Employee ID: EMP002
✓ Created: Vamika Singh (vamika@believersdestination.com) | Employee ID: EMP003
✓ Created: Shubh Saxena (shubh.saxena@believersdestination.com) | Employee ID: EMP004
✓ Created: Nikita Sharma (nikita@believersdestination.com) | Employee ID: EMP005

Summary: 5 created, 0 skipped
============================================================
```

---

## Phase 2 🔄 - Device Import

### Command
```bash
python manage.py load_devices
```

### Options
```bash
# Load from custom file
python manage.py load_devices --file /path/to/devices.json

# Delete all existing devices and reload
python manage.py load_devices --delete
```

### Devices Imported from inventory.json

**Laptops:**
- LAP001: Apple MacBook Air M1 (8GB RAM, 256GB SSD)
- LAP002: Lenovo ThinkPad E14 (16GB RAM, 512GB SSD)
- LAP003: HP Pavilion 15 (16GB RAM, 512GB SSD)
- LAP004: Lenovo IdeaPad Slim 5 (8GB RAM, 512GB SSD)
- LAP005: HP EliteBook 840 (16GB RAM, 1TB SSD)

**Peripherals:**
- MOU001: HP Wireless Mouse
- MOU002: Lenovo Wired Mouse
- MOU003: Logitech Wireless Mouse
- KEY001: HP Wired Keyboard
- KEY002: Lenovo Wireless Keyboard

**SIM Cards:**
- SIM001: Airtel (Qty: 5)
- SIM002: Jio (Qty: 5)

### Expected Output
```
============================================================
Loading devices from: inventry.json
✓ Created: Apple MacBook Air M1 (LAP001) | Type: laptop
✓ Created: Lenovo ThinkPad E14 (LAP002) | Type: laptop
... (more devices)

Summary: 16 created, 0 skipped
============================================================
```

---

## API Testing Guide

### 1. User Authentication (Phase 1)

#### Login User
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "arun.gautam@believersdestination.com",
    "password": "TestPass@123"
  }'
```

**Response:**
```json
{
  "message": "Login successful",
  "employee": {
    "id": "uuid",
    "email": "arun.gautam@believersdestination.com",
    "first_name": "Arun",
    "last_name": "Gautam",
    "employee_id": "EMP001",
    "role": "employee",
    "email_verified": false
  },
  "tokens": {
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGc..."
  }
}
```

**Save the `access` token for subsequent requests!**

---

### 2. Email Verification (Phase 1.1)

#### Send OTP
```bash
curl -X POST http://localhost:8000/api/auth/email/send-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "arun.gautam@believersdestination.com"
  }'
```

**Response:**
```json
{
  "message": "OTP has been sent to your email",
  "email": "arun.gautam@believersdestination.com"
}
```

**Note:** In development, OTP will be printed to console. In production, it's sent via email.

#### Verify OTP
```bash
curl -X POST http://localhost:8000/api/auth/email/verify-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "arun.gautam@believersdestination.com",
    "otp": "123456"
  }'
```

**Response:**
```json
{
  "message": "Email verified successfully",
  "employee": {
    "id": "uuid",
    "email": "arun.gautam@believersdestination.com",
    "email_verified": true,
    ...
  }
}
```

#### Change Password After Verification
```bash
curl -X POST http://localhost:8000/api/auth/email/change-password/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "arun.gautam@believersdestination.com",
    "otp": "123456",
    "new_password": "NewSecurePass@123"
  }'
```

**Response:**
```json
{
  "message": "Password changed successfully"
}
```

---

### 3. View Devices (Phase 2)

#### Get All Available Devices
```bash
curl -X GET http://localhost:8000/api/inventory/devices/?status=available \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

**Response:**
```json
{
  "count": 16,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "device_id": "LAP001",
      "name": "Apple MacBook Air M1",
      "device_type": "laptop",
      "brand": "Apple",
      "model": "MacBook Air M1",
      "status": "available",
      "condition": "new"
    },
    ...
  ]
}
```

#### Get Specific Device Type
```bash
curl -X GET http://localhost:8000/api/inventory/devices/?status=available&device_type=laptop \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

---

### 4. Device Request & Approval (Phase 3)

#### Request a Device
```bash
curl -X POST http://localhost:8000/api/inventory/device-requests/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "device_type": "laptop",
    "brand": "HP",
    "model": "EliteBook",
    "specifications": {
      "ram": "16GB",
      "storage": "512GB"
    },
    "reason": "Project development work for Q2 2024"
  }'
```

**Response:**
```json
{
  "id": "uuid",
  "requested_by": "arun.gautam@believersdestination.com",
  "device_type": "laptop",
  "brand": "HP",
  "model": "EliteBook",
  "reason": "Project development work for Q2 2024",
  "status": "pending",
  "created_at": "2024-04-23T10:30:00Z"
}
```

#### View Pending Requests (Admin Only)
```bash
curl -X GET http://localhost:8000/api/inventory/device-requests/?status=pending \
  -H "Authorization: Bearer {ADMIN_ACCESS_TOKEN}"
```

#### Approve Request
```bash
curl -X POST http://localhost:8000/api/inventory/device-requests/{REQUEST_ID}/approve/ \
  -H "Authorization: Bearer {ADMIN_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response:**
```json
{
  "message": "Device request approved and assignment created",
  "request": {
    "status": "approved",
    ...
  },
  "assignment_id": "uuid"
}
```

#### Reject Request
```bash
curl -X POST http://localhost:8000/api/inventory/device-requests/{REQUEST_ID}/reject/ \
  -H "Authorization: Bearer {ADMIN_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "rejection_reason": "Device not available currently"
  }'
```

---

### 5. Consent Form Submission (Phase 3.1)

#### Submit Consent Form
```bash
curl -X POST http://localhost:8000/api/inventory/assignments/{ASSIGNMENT_ID}/submit-consent/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "consent_form_data": {
      "condition_at_receipt": "good",
      "acknowledgment": true,
      "signature": "base64_encoded_signature_or_url"
    },
    "consent_images": [
      "https://example.com/image1.jpg",
      "https://example.com/image2.jpg"
    ]
  }'
```

**Response:**
```json
{
  "message": "Consent form submitted successfully",
  "assignment": {
    "id": "uuid",
    "status": "consent_pending",
    "consent_form_data": {...},
    "consent_images": [...]
  }
}
```

#### Admin Approves Consent (Admin Only)
```bash
curl -X POST http://localhost:8000/api/inventory/assignments/{ASSIGNMENT_ID}/approve-consent/ \
  -H "Authorization: Bearer {ADMIN_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response:**
```json
{
  "message": "Consent approved successfully",
  "assignment": {
    "status": "active",
    "consent_approved": true,
    "consent_approved_at": "2024-04-23T11:00:00Z"
  }
}
```

---

### 6. Device Grant with Email Notification (Phase 4.1) ⭐

#### Grant Device to User
```bash
curl -X POST http://localhost:8000/api/inventory/assignments/{ASSIGNMENT_ID}/grant-device/ \
  -H "Authorization: Bearer {ADMIN_ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{}'
```

**Response:**
```json
{
  "message": "Device granted successfully and notifications sent",
  "assignment": {
    "id": "uuid",
    "status": "active",
    "device": {
      "device_id": "LAP001",
      "name": "Apple MacBook Air M1"
    },
    "employee": {
      "email": "arun.gautam@believersdestination.com",
      "full_name": "Arun Kumar Gautam"
    }
  },
  "emails_sent_to": [
    "arun.gautam@believersdestination.com",
    "jagruti@believersdestination.com",
    "kunal@believersdestination.com",
    "varun@believersdestination.com",
    "chahat.gupta@believersdestination.com"
  ]
}
```

**Emails Sent:**
1. **To Employee:** Device assignment notification with full details
2. **To Admin/HR:** Device grant confirmation and record

---

## Admin Dashboard Endpoints

### Get All Pending Requests
```bash
curl -X GET http://localhost:8000/api/inventory/device-requests/?status=pending \
  -H "Authorization: Bearer {ADMIN_ACCESS_TOKEN}"
```

### Get All Pending Consents
```bash
curl -X GET http://localhost:8000/api/inventory/assignments/?status=consent_pending \
  -H "Authorization: Bearer {ADMIN_ACCESS_TOKEN}"
```

### Get Dashboard Statistics
```bash
curl -X GET http://localhost:8000/api/inventory/dashboard/ \
  -H "Authorization: Bearer {ADMIN_ACCESS_TOKEN}"
```

**Response:**
```json
{
  "count": 1,
  "results": [
    {
      "total_devices": 16,
      "available_devices": 15,
      "assigned_devices": 1,
      "maintenance_devices": 0,
      "total_employees": 5,
      "active_assignments": 1,
      "pending_tickets": 0,
      "resolved_tickets": 0
    }
  ]
}
```

---

## Complete User Journey - Test Flow

### Step 1: User Signup & Email Verification (Frontend)
```
User navigates to signup page → Fills form → Receives OTP via email → 
Enters OTP → Changes initial password (optional)
```

### Step 2: User Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -d '{"email": "arun.gautam@believersdestination.com", "password": "TestPass@123"}'
```

### Step 3: User Views Available Devices
```bash
curl -X GET http://localhost:8000/api/inventory/devices/?status=available \
  -H "Authorization: Bearer {TOKEN}"
```

### Step 4: User Requests Device
```bash
curl -X POST http://localhost:8000/api/inventory/device-requests/ \
  -H "Authorization: Bearer {TOKEN}" \
  -d '{"device_type": "laptop", "reason": "Project work"}'
```

### Step 5: Admin Views Pending Requests
```bash
curl -X GET http://localhost:8000/api/inventory/device-requests/?status=pending \
  -H "Authorization: Bearer {ADMIN_TOKEN}"
```

### Step 6: Admin Approves Request
```bash
curl -X POST http://localhost:8000/api/inventory/device-requests/{REQUEST_ID}/approve/ \
  -H "Authorization: Bearer {ADMIN_TOKEN}"
```
**→ Assignment created automatically**
**→ User receives notification email**

### Step 7: User Submits Consent Form
```bash
curl -X POST http://localhost:8000/api/inventory/assignments/{ASSIGNMENT_ID}/submit-consent/ \
  -H "Authorization: Bearer {TOKEN}" \
  -d '{"consent_form_data": {...}, "consent_images": [...]}'
```

### Step 8: Admin Reviews Consent & Approves
```bash
curl -X POST http://localhost:8000/api/inventory/assignments/{ASSIGNMENT_ID}/approve-consent/ \
  -H "Authorization: Bearer {ADMIN_TOKEN}"
```
**→ Status changes to active**
**→ Device is now assigned**

### Step 9: Admin Grants Device
```bash
curl -X POST http://localhost:8000/api/inventory/assignments/{ASSIGNMENT_ID}/grant-device/ \
  -H "Authorization: Bearer {ADMIN_TOKEN}"
```
**→ Email notifications sent to:**
  - Employee (device assignment confirmation)
  - HR team (jagruti@believersdestination.com)
  - Admin (kunal@believersdestination.com)
  - Finance (varun@believersdestination.com)
  - HR Manager (chahat.gupta@believersdestination.com)

### Step 10: Device Appears in User's Dashboard
```bash
curl -X GET http://localhost:8000/api/inventory/assignments/my-assignments/ \
  -H "Authorization: Bearer {TOKEN}"
```
Shows: Device ID, Device Details, Assignment Date, Status: Active

---

## Postman Collection

Save this as `ims-api.postman_collection.json`:

```json
{
  "info": {
    "name": "IMS API Collection",
    "version": "1.0.0"
  },
  "item": [
    {
      "name": "Authentication",
      "item": [
        {
          "name": "Login",
          "request": {
            "method": "POST",
            "url": "{{baseUrl}}/api/auth/login/",
            "body": {
              "email": "arun.gautam@believersdestination.com",
              "password": "TestPass@123"
            }
          }
        },
        {
          "name": "Send OTP",
          "request": {
            "method": "POST",
            "url": "{{baseUrl}}/api/auth/email/send-otp/"
          }
        }
      ]
    },
    {
      "name": "Inventory",
      "item": [
        {
          "name": "Get Available Devices",
          "request": {
            "method": "GET",
            "url": "{{baseUrl}}/api/inventory/devices/?status=available"
          }
        },
        {
          "name": "Request Device",
          "request": {
            "method": "POST",
            "url": "{{baseUrl}}/api/inventory/device-requests/"
          }
        }
      ]
    }
  ]
}
```

---

## Environment Variables (.env)

Create `.env` file in `ims-backendd/` directory:

```
# Debug & Security
DEBUG=True
SECRET_KEY=your-django-secret-key

# Database (if using PostgreSQL)
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3

# Email (using Apps Script)
APPS_SCRIPT_URL=https://script.google.com/macros/d/YOUR_SCRIPT_ID/usercontent
APPS_SCRIPT_API_KEY=your-api-key

# Email (fallback SMTP)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Frontend
FRONTEND_URL=http://localhost:5173

# JWT
JWT_SECRET_KEY=your-jwt-secret
```

---

## Troubleshooting

### OTP not being sent
- Check EMAIL_BACKEND in settings (should be console in development)
- Check Django console output for OTP
- Ensure email service is configured

### Device not appearing in assignments
- Verify device status is "available"
- Check if device_type matches request

### Email notifications not received
- Verify ADMIN_EMAIL_RECIPIENTS in settings.py
- Check email service configuration
- Review Apps Script URL and API key

### Permission denied errors
- Ensure you're using correct access token
- Check user role (admin vs employee)
- Verify JWT token hasn't expired

---

## Next Steps

1. ✅ Run `create_test_users`
2. ✅ Run `load_devices`
3. 🔄 Test all endpoints above
4. ⏳ Build frontend components (signup, login, device request form, etc.)
5. ⏳ Create AppScript integration for advanced inventory management
6. ⏳ Set up production email service (Gmail, SendGrid, etc.)

**Now test the complete flow from signup to device grant! 🚀**
