# IMS Complete Implementation Guide

## Overview
Building a comprehensive Inventory Management System with complete device lifecycle management, from user authentication to device assignment with email notifications.

---

## PHASES IMPLEMENTATION PLAN

### Phase 1 ✅ - User Creation & Auth Flow (COMPLETED)
- [x] Employee model with email-based authentication
- [x] Role-based access (admin, manager, employee)
- [x] Employee ID auto-generation

**Implementation:**
```bash
# Create test users
python manage.py create_test_users

# Optional: Delete and recreate
python manage.py create_test_users --delete
```

**Test Users Created:**
1. Arun Kumar Gautam (arun.gautam@believersdestination.com) - IT
2. Vikas Chauhan (vikas.chauhan@believersdestination.com) - IT  
3. Vamika Singh (vamika@believersdestination.com) - HR
4. Shubh Saxena (shubh.saxena@believersdestination.com) - IT
5. Nikita Sharma (nikita@believersdestination.com) - Operations

Default Password: `TestPass@123`

---

### Phase 1.1 ✅ - Email Verification with OTP (READY)

**API Endpoints:**
- `POST /api/auth/email/send-otp/` - Send OTP to email
- `POST /api/auth/email/verify-otp/` - Verify OTP
- `POST /api/auth/email/change-password/` - Change password after verification

**Request/Response Examples:**

1. **Send OTP:**
```json
POST /api/auth/email/send-otp/
{
  "email": "user@believersdestination.com"
}
Response:
{
  "message": "OTP has been sent to your email",
  "email": "user@believersdestination.com"
}
```

2. **Verify OTP:**
```json
POST /api/auth/email/verify-otp/
{
  "email": "user@believersdestination.com",
  "otp": "123456"
}
Response:
{
  "message": "Email verified successfully",
  "employee": { ...employee data... }
}
```

3. **Change Password After Verification:**
```json
POST /api/auth/email/change-password/
{
  "email": "user@believersdestination.com",
  "otp": "123456",
  "new_password": "NewSecurePass@123"
}
Response:
{
  "message": "Password changed successfully"
}
```

---

### Phase 2 🔄 - Device Import from Inventory.json

**Implementation:**
```bash
# Load devices from inventory.json
python manage.py load_devices

# Or specify custom file
python manage.py load_devices --file /path/to/devices.json

# Delete existing devices first
python manage.py load_devices --delete
```

**Supported Device Categories from inventory.json:**
- Laptops (LAP001-LAP005)
- Mice (MOU001-MOU003)
- Keyboards (KEY001-KEY002)
- SIM Cards (SIM001-SIM002)
- PC Setups (PC001+)

**Device Status States:**
- `available` - Ready for assignment
- `assigned` - Currently assigned to user
- `maintenance` - Under repair
- `retired` - No longer in use

---

### Phase 2.1 🔄 - AppScript Integration

**Endpoints to be created:**
```
POST /api/inventory/appscript/sync/
POST /api/inventory/appscript/auth-sync/
```

**AppScript Setup Steps:**
1. Create Google Apps Script in your Google Drive
2. Deploy as Web App
3. Configure webhook URL in Django settings
4. Test sync endpoint

---

### Phase 3 🔄 - Device Request & Approval Flow

**User Flow:**
1. User views available devices
2. User requests a device
3. Admin receives notification
4. Admin reviews and approves/rejects
5. User gets notification

**API Endpoints:**

#### Request Device
```json
POST /api/inventory/device-requests/
{
  "device_type": "laptop",
  "brand": "HP",
  "model": "EliteBook",
  "specifications": {
    "ram": "16GB",
    "storage": "512GB"
  },
  "reason": "Project development work"
}
Response:
{
  "id": "uuid",
  "requested_by": "user_email",
  "device_type": "laptop",
  "status": "pending",
  "created_at": "2024-04-23T..."
}
```

#### View Pending Requests (Admin)
```
GET /api/inventory/device-requests/?status=pending
```

#### Approve Request
```json
POST /api/inventory/device-requests/{id}/approve/
{}
Response:
{
  "message": "Request approved",
  "status": "approved"
}
```

#### Reject Request
```json
POST /api/inventory/device-requests/{id}/reject/
{}
```

---

### Phase 3.1 🔄 - Consent Form Implementation

**Consent Form Flow:**
1. Admin approves device request
2. User gets consent form popup
3. User fills and submits form
4. Admin reviews consent form
5. Admin approves final assignment

**Form Fields:**
- Employee Name (auto-filled)
- Employee ID (auto-filled)
- Device ID
- Device Specifications
- Condition at Receipt (checkbox/photo)
- Acknowledgment checkbox
- Signature (digital)
- Timestamp

**API Endpoints:**

#### Submit Consent Form
```json
POST /api/inventory/assignments/{id}/submit-consent/
{
  "consent_form_data": {
    "condition_at_receipt": "good",
    "acknowledgment": true,
    "signature": "base64_or_url"
  },
  "consent_images": ["image_url1", "image_url2"]
}
```

#### Approve Consent Form (Admin)
```json
POST /api/inventory/assignments/{id}/approve-consent/
{}
```

---

### Phase 4 🔄 - Admin Dashboard

**Admin Features:**
- Pending requests list
- Pending consent forms
- Device assignment management
- Device grant button
- View all assignments
- Search and filter

**Admin URL:** `/admin/` (Already configured)

**Admin Dashboard Endpoints:**
```
GET /api/inventory/dashboard/
GET /api/inventory/assignments/?status=pending_approval
GET /api/inventory/assignments/?status=consent_pending
```

---

### Phase 4.1 🔄 - Device Grant & Email System

**Device Grant Flow:**
1. Admin reviews consent form
2. Admin clicks "Device Grant" button
3. System sends email to:
   - Device Owner (user)
   - HR (jagruti@believersdestination.com)
   - Admin (kunal@believersdestination.com)
   - Finance (varun@believersdestination.com)
   - HR Manager (chahat.gupta@believersdestination.com)
4. Assignment status changes to "active"

**API Endpoint:**
```json
POST /api/inventory/assignments/{id}/grant-device/
{}
Response:
{
  "message": "Device granted successfully",
  "status": "active",
  "email_sent_to": ["email1", "email2", ...]
}
```

**Email Template:**
```
Subject: Device Assignment Notification - [Device_ID]

Body:
---
Dear [Employee Name],

Your device request has been approved and the following device has been assigned to you:

Device Details:
- Device ID: [DEVICE_ID]
- Device Type: [TYPE]
- Brand & Model: [BRAND] [MODEL]
- Assignment Date: [DATE]
- Expected Return Date: [DATE]

Please confirm receipt and condition of the device.

Terms:
- Device remains property of [Company]
- Device must be returned in good condition
- Report any issues immediately

Admin Contact: [ADMIN_EMAIL]

---
CC: HR Team, Finance
```

---

## Complete User Journey: Signup to Device Grant

```
1. SIGNUP (Frontend)
   └─> POST /api/auth/signup/
       ├─ Email, Name, Password
       ├─ Auto-generates Employee ID (EMP001, EMP002...)
       └─ Sends Welcome Email

2. EMAIL VERIFICATION (Frontend Popup)
   ├─> POST /api/auth/email/send-otp/
   │   └─ Receive OTP in email
   ├─> POST /api/auth/email/verify-otp/
   │   ├─ Enter OTP
   │   └─ Mark email as verified
   └─> POST /api/auth/email/change-password/ (optional)

3. LOGIN (Frontend)
   ├─> POST /api/auth/login/
   │   ├─ Email & Password
   │   └─ Receive JWT tokens

4. VIEW AVAILABLE DEVICES (User Dashboard)
   └─> GET /api/inventory/devices/?status=available
       └─ See laptops, accessories, etc.

5. REQUEST DEVICE (User)
   └─> POST /api/inventory/device-requests/
       ├─ Specify device type & reason
       └─ Status: pending

6. ADMIN APPROVAL (Admin Dashboard)
   ├─> GET /api/inventory/device-requests/?status=pending
   ├─> Review request
   └─> POST /api/inventory/device-requests/{id}/approve/
       └─ Status: approved → User notified

7. CONSENT FORM (User Popup)
   ├─> User receives notification
   ├─> Opens consent form
   └─> POST /api/inventory/assignments/{id}/submit-consent/
       └─ Submit with device photos/signature

8. ADMIN CONSENT REVIEW (Admin Dashboard)
   ├─> GET /api/inventory/assignments/?status=consent_pending
   ├─> Review form
   └─> POST /api/inventory/assignments/{id}/approve-consent/
       └─ Form approved

9. DEVICE GRANT (Admin)
   ├─> POST /api/inventory/assignments/{id}/grant-device/
   ├─ Email sent to: Owner, HR, Admin, Finance
   └─> Status: active

10. USER RECEIVES DEVICE
    └─> Device appears in "My Assigned Devices"
        ├─ Assignment Date: [DATE]
        ├─ Return Date: [When user assigned, perpetual for PC]
        └─ Status: Active
```

---

## Key Settings Required in Django

```python
# settings.py

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'app-password'
DEFAULT_FROM_EMAIL = 'noreply@believersdestination.com'

# Apps Script Integration
APPS_SCRIPT_URL = 'https://script.google.com/macros/d/{SCRIPT_ID}/usercontent'
APPS_SCRIPT_API_KEY = 'your-api-key'

# JWT Configuration
JWT_AUTH_COOKIE = 'jwt_auth_secure'
JWT_AUTH_REFRESH_COOKIE = 'jwt_refresh_secure'

# Admin Recipients for Email Notifications
ADMIN_EMAIL_RECIPIENTS = [
    'jagruti@believersdestination.com',
    'kunal@believersdestination.com',
    'varun@believersdestination.com',
    'chahat.gupta@believersdestination.com',
]
```

---

## Database Migrations Checklist

```bash
python manage.py makemigrations
python manage.py migrate

# Create superuser if not exists
python manage.py createsuperuser

# Create test users
python manage.py create_test_users

# Load devices
python manage.py load_devices
```

---

## Testing Endpoints

### 1. Create Test Users
```bash
python manage.py create_test_users
```

### 2. Login & Get Token
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "arun.gautam@believersdestination.com",
    "password": "TestPass@123"
  }'
```

### 3. Send OTP
```bash
curl -X POST http://localhost:8000/api/auth/email/send-otp/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "arun.gautam@believersdestination.com"
  }'
```

### 4. Get Available Devices
```bash
curl -X GET http://localhost:8000/api/inventory/devices/?status=available \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 5. Request Device
```bash
curl -X POST http://localhost:8000/api/inventory/device-requests/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "device_type": "laptop",
    "brand": "HP",
    "specifications": {"ram": "16GB"},
    "reason": "Project work"
  }'
```

---

## Environment Variables (.env)

```
DEBUG=False
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=ims_db
DB_USER=postgres
DB_PASSWORD=your-password
DB_HOST=localhost
DB_PORT=5432

# Email
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=app-password

# Apps Script
APPS_SCRIPT_URL=https://script.google.com/...
APPS_SCRIPT_API_KEY=your-key

# JWT
JWT_SECRET_KEY=your-secret-key
```

---

## Current Status

| Phase | Status | Tasks |
|-------|--------|-------|
| 1 | ✅ Ready | Create test users |
| 1.1 | ✅ Ready | Email verification endpoints live |
| 2 | 🔄 Next | Load devices from JSON |
| 2.1 | ⏳ Queue | AppScript integration |
| 3 | ⏳ Queue | Device request workflow |
| 3.1 | ⏳ Queue | Consent form system |
| 4 | ⏳ Queue | Admin dashboard |
| 4.1 | ⏳ Queue | Device grant emails |

---

## Files to Modify/Create

### Already Ready
- ✅ `apps/authentication/management/commands/create_test_users.py`
- ✅ `apps/inventory/management/commands/load_devices.py`
- ✅ Email OTP models & views

### Need Completion
- [ ] Device request views & serializers (API endpoints)
- [ ] Consent form views & serializers
- [ ] Assignment approval views
- [ ] Email notification templates & service
- [ ] Admin dashboard API
- [ ] Device grant email system
- [ ] Frontend components (popups, forms, pages)

---

## Next Steps

1. ✅ Create test users → `python manage.py create_test_users`
2. ✅ Load devices → `python manage.py load_devices`
3. ⏳ Enhance device request views with approval logic
4. ⏳ Create consent form endpoints
5. ⏳ Set up email templates
6. ⏳ Create admin dashboard endpoints
7. ⏳ Build device grant email system
8. ⏳ Frontend implementation

---

**Ready to execute?** Run the management commands to set up Phase 1 & 2!
