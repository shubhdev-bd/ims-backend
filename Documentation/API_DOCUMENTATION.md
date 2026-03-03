# Inventory Management System (IMS) - Backend API Documentation

**Version:** 1.0.0  
**Last Updated:** March 2, 2026
**Backend URL:** https://ims-backend-e4fp.onrender.com/api  
**Frontend URL:** https://ims-frontend-lilac-alpha.vercel.app

---

## Table of Contents
1. [Authentication APIs](#authentication-apis)
2. [Inventory APIs](#inventory-apis)
3. [Data Models](#data-models)
4. [Error Handling](#error-handling)
5. [Deployment Guide](#deployment-guide)

---

## Authentication APIs

### Base URL
```
/api/auth/
```

### 1. User Signup
**Endpoint:** `POST /api/auth/signup/`

**Request Body:**
```json
{
  "email": "employee@company.com",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "department": "IT",
  "phone_number": "+1-555-0123"
}
```

**Response (201 Created):**
```json
{
  "message": "Account created successfully",
  "employee": {
    "id": "uuid",
    "email": "employee@company.com",
    "first_name": "John",
    "last_name": "Doe",
    "department": "IT",
    "role": "employee",
    "phone_number": "+1-555-0123",
    "date_joined": "2026-03-02T10:00:00Z"
  },
  "tokens": {
    "refresh": "refresh_token_string",
    "access": "access_token_string"
  }
}
```

**Required Departments:**
- IT (Information Technology)
- HR (Human Resources)
- Finance
- Operations
- Sales
- Marketing

---

### 2. User Login
**Endpoint:** `POST /api/auth/login/`

**Request Body:**
```json
{
  "email": "employee@company.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "message": "Login successful",
  "employee": {
    "id": "uuid",
    "email": "employee@company.com",
    "first_name": "John",
    "last_name": "Doe",
    "role": "employee",
    "department": "IT"
  },
  "tokens": {
    "refresh": "refresh_token_string",
    "access": "access_token_string"
  }
}
```

---

### 3. User Logout
**Endpoint:** `POST /api/auth/logout/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "refresh_token": "refresh_token_string"
}
```

**Response (200 OK):**
```json
{
  "message": "Logout successful"
}
```

---

### 4. Get Current User Profile
**Endpoint:** `GET /api/auth/me/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "email": "employee@company.com",
  "first_name": "John",
  "last_name": "Doe",
  "role": "employee",
  "department": "IT",
  "phone_number": "+1-555-0123",
  "is_active": true,
  "date_joined": "2026-03-02T10:00:00Z"
}
```

---

### 5. Update Profile
**Endpoint:** `PATCH /api/auth/me/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body (all fields optional):**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1-555-0123",
  "department": "IT"
}
```

**Response (200 OK):**
```json
{
  "message": "Profile updated successfully",
  "employee": { /* updated employee object */ }
}
```

---

### 6. Change Password
**Endpoint:** `POST /api/auth/password/change/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "old_password": "oldpassword123",
  "new_password": "newpassword123",
  "confirm_password": "newpassword123"
}
```

**Response (200 OK):**
```json
{
  "message": "Password changed successfully"
}
```

---

### 7. Request Password Reset
**Endpoint:** `POST /api/auth/password/reset/`

**Request Body:**
```json
{
  "email": "employee@company.com"
}
```

**Response (200 OK):**
```json
{
  "message": "Password reset link sent to your email"
}
```

---

### 8. Confirm Password Reset
**Endpoint:** `POST /api/auth/password/reset/confirm/`

**Request Body:**
```json
{
  "token": "reset_token_from_email",
  "password": "newpassword123",
  "confirm_password": "newpassword123"
}
```

**Response (200 OK):**
```json
{
  "message": "Password reset successfully"
}
```

---

### 9. Verify Reset Token
**Endpoint:** `GET /api/auth/password/reset/verify/?token={reset_token}`

**Response (200 OK):**
```json
{
  "message": "Token is valid"
}
```

---

### 10. Refresh Token
**Endpoint:** `POST /api/auth/token/refresh/`

**Request Body:**
```json
{
  "refresh": "refresh_token_string"
}
```

**Response (200 OK):**
```json
{
  "access": "new_access_token_string"
}
```

---

## Inventory APIs

### Base URL
```
/api/inventory/
```

---

## Device Management

### 1. List All Devices
**Endpoint:** `GET /api/inventory/devices/`

**Query Parameters:**
- `status` - Filter by status: `available`, `assigned`, `maintenance`, `retired`
- `device_type` - Filter by type: `laptop`, `desktop`, `monitor`, `keyboard`, `mouse`, `headset`, `phone`, `tablet`, `other`
- `condition` - Filter by condition: `new`, `excellent`, `good`, `fair`, `poor`
- `search` - Search by device_id, name, brand, model, serial_number
- `ordering` - Sort by: `created_at`, `name`, `status`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
[
  {
    "id": "uuid",
    "device_id": "DEV001",
    "name": "MacBook Pro 16",
    "device_type": "laptop",
    "brand": "Apple",
    "model": "M3 Max",
    "serial_number": "SN12345678",
    "status": "assigned",
    "condition": "excellent",
    "purchase_date": "2025-01-15",
    "warranty_expiry": "2027-01-15",
    "location": "Office A",
    "created_at": "2026-01-15T10:00:00Z"
  }
]
```

---

### 2. Get Device Details
**Endpoint:** `GET /api/inventory/devices/{id}/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "device_id": "DEV001",
  "name": "MacBook Pro 16",
  "device_type": "laptop",
  "brand": "Apple",
  "model": "M3 Max",
  "serial_number": "SN12345678",
  "status": "assigned",
  "condition": "excellent",
  "specifications": {
    "processor": "Apple M3 Max",
    "ram": "36GB",
    "storage": "1TB SSD"
  },
  "purchase_date": "2025-01-15",
  "purchase_price": "3499.00",
  "warranty_expiry": "2027-01-15",
  "location": "Office A",
  "notes": "Primary development device",
  "created_at": "2026-01-15T10:00:00Z",
  "updated_at": "2026-02-20T14:30:00Z"
}
```

---

### 3. Create Device (Admin Only)
**Endpoint:** `POST /api/inventory/devices/`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "device_id": "DEV002",
  "name": "Dell XPS 15",
  "device_type": "laptop",
  "brand": "Dell",
  "model": "XPS 15-9530",
  "serial_number": "SN87654321",
  "status": "available",
  "condition": "excellent",
  "specifications": {
    "processor": "Intel i9",
    "ram": "32GB",
    "storage": "1TB SSD"
  },
  "purchase_date": "2025-06-01",
  "purchase_price": "2499.00",
  "warranty_expiry": "2027-06-01",
  "location": "Office B"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "device_id": "DEV002",
  "name": "Dell XPS 15"
  /* ... full device object ... */
}
```

---

### 4. Update Device (Admin Only)
**Endpoint:** `PATCH /api/inventory/devices/{id}/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body (partial update):**
```json
{
  "status": "maintenance",
  "condition": "fair",
  "location": "Repair Center"
}
```

**Response (200 OK):**
```json
{ /* updated device object */ }
```

---

### 5. Delete Device (Admin Only)
**Endpoint:** `DELETE /api/inventory/devices/{id}/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (204 No Content)**

---

### 6. Get Available Devices
**Endpoint:** `GET /api/inventory/devices/available/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
[
  { /* device objects with status 'available' */ }
]
```

---

### 7. Mark Device as Maintenance
**Endpoint:** `POST /api/inventory/devices/{id}/mark_maintenance/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "message": "Device marked as under maintenance",
  "device": { /* updated device object */ }
}
```

---

### 8. Mark Device as Available
**Endpoint:** `POST /api/inventory/devices/{id}/mark_available/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "message": "Device marked as available",
  "device": { /* updated device object */ }
}
```

---

## Device Assignment

### 1. List All Assignments
**Endpoint:** `GET /api/inventory/assignments/`

**Query Parameters:**
- `status` - Filter by: `active`, `returned`, `lost`, `damaged`
- `employee` - Filter by employee UUID
- `device` - Filter by device UUID

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
[
  {
    "id": "uuid",
    "device": { /* device object */ },
    "employee": { /* employee object */ },
    "status": "active",
    "assigned_date": "2026-02-01T09:00:00Z",
    "expected_return_date": "2027-02-01",
    "assigned_by": { /* admin/manager who assigned */ }
  }
]
```

---

### 2. Create Assignment (Admin/Manager Only)
**Endpoint:** `POST /api/inventory/assignments/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "device": "device_uuid",
  "employee": "employee_uuid",
  "expected_return_date": "2027-02-01",
  "assignment_notes": "Office equipment for new project"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "device": { /* device object */ },
  "employee": { /* employee object */ },
  "status": "active",
  "assigned_date": "2026-03-02T10:00:00Z"
  /* ... full assignment object ... */
}
```

---

### 3. Return Device
**Endpoint:** `POST /api/inventory/assignments/{id}/return_device/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "return_notes": "Device returned in good condition"
}
```

**Response (200 OK):**
```json
{
  "message": "Device returned successfully",
  "assignment": { /* updated assignment object */ }
}
```

---

### 4. Get My Assignments
**Endpoint:** `GET /api/inventory/assignments/my_assignments/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
[
  { /* assignments for current user */ }
]
```

---

## Ticket Management

### 1. List All Tickets
**Endpoint:** `GET /api/inventory/tickets/`

**Query Parameters:**
- `status` - Filter by: `pending`, `in_progress`, `resolved`, `rejected`, `closed`
- `ticket_type` - Filter by: `repair`, `replacement`, `new_device`, `issue`, `return`, `other`
- `priority` - Filter by: `low`, `medium`, `high`, `urgent`
- `search` - Search by ticket_number, subject

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
[
  {
    "id": "uuid",
    "ticket_number": "TKT001",
    "subject": "Laptop Screen Broken",
    "ticket_type": "repair",
    "priority": "high",
    "status": "in_progress",
    "requested_by": { /* employee who created */ },
    "assigned_to": { /* admin/manager assigned */ },
    "device": { /* related device if any */ },
    "created_at": "2026-03-01T14:00:00Z"
  }
]
```

---

### 2. Create Ticket (Issue/Repair Request)
**Endpoint:** `POST /api/inventory/tickets/`

**Headers:**
```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**
```json
{
  "ticket_type": "repair",
  "priority": "high",
  "subject": "Laptop Screen Broken",
  "description": "The laptop display is cracked and needs replacement",
  "device": "device_uuid"
}
```

**Response (201 Created):**
```json
{
  "id": "uuid",
  "ticket_number": "TKT001",
  "subject": "Laptop Screen Broken",
  "ticket_type": "repair",
  "priority": "high",
  "status": "pending",
  "requested_by": { /* current user */ },
  "created_at": "2026-03-02T10:00:00Z"
  /* ... full ticket object ... */
}
```

---

### 3. Get Ticket Details
**Endpoint:** `GET /api/inventory/tickets/{id}/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "id": "uuid",
  "ticket_number": "TKT001",
  "subject": "Laptop Screen Broken",
  "description": "The laptop display is cracked and needs replacement",
  "ticket_type": "repair",
  "priority": "high",
  "status": "in_progress",
  "requested_by": { /* employee object */ },
  "assigned_to": { /* manager/admin object */ },
  "device": { /* device object if related */ },
  "resolution_notes": "",
  "created_at": "2026-03-02T10:00:00Z",
  "updated_at": "2026-03-02T14:00:00Z"
}
```

---

### 4. Assign Ticket (Admin/Manager Only)
**Endpoint:** `POST /api/inventory/tickets/{id}/assign/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "assigned_to": "employee_uuid"
}
```

**Response (200 OK):**
```json
{
  "message": "Ticket assigned to John Doe",
  "ticket": { /* updated ticket object */ }
}
```

---

### 5. Resolve Ticket (Admin/Manager Only)
**Endpoint:** `POST /api/inventory/tickets/{id}/resolve/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "resolution_notes": "Screen replaced successfully. Device tested and working properly."
}
```

**Response (200 OK):**
```json
{
  "message": "Ticket resolved successfully",
  "ticket": { /* updated ticket with status 'resolved' */ }
}
```

---

### 6. Get My Tickets
**Endpoint:** `GET /api/inventory/tickets/my_tickets/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
[
  { /* tickets created by current user */ }
]
```

---

## Dashboard

### Get Dashboard Statistics
**Endpoint:** `GET /api/inventory/dashboard/stats/`

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response (200 OK):**
```json
{
  "total_devices": 45,
  "available_devices": 12,
  "assigned_devices": 28,
  "maintenance_devices": 4,
  "retired_devices": 1,
  "total_employees": 25,
  "active_employees": 20,
  "total_assignments": 30,
  "active_assignments": 28,
  "total_tickets": 15,
  "pending_tickets": 3,
  "in_progress_tickets": 5,
  "resolved_tickets": 7,
  "device_by_type": {
    "laptop": 20,
    "desktop": 15,
    "monitor": 10
  },
  "recent_assignments": [ /* last 5 assignments */ ],
  "recent_tickets": [ /* last 5 tickets */ ]
}
```

---

## Data Models

### Employee Model
```json
{
  "id": "UUID",
  "email": "string (unique, required)",
  "first_name": "string (required)",
  "last_name": "string (required)",
  "employee_id": "string (unique, optional)",
  "role": "admin|manager|employee (default: employee)",
  "department": "IT|HR|Finance|Operations|Sales|Marketing (optional)",
  "phone_number": "string (optional)",
  "is_active": "boolean (default: true)",
  "is_staff": "boolean (default: false)",
  "date_joined": "datetime (auto)",
  "last_login": "datetime (nullable)",
  "profile_picture": "file (optional)"
}
```

### Device Model
```json
{
  "id": "UUID",
  "device_id": "string (unique, required)",
  "name": "string (required)",
  "device_type": "laptop|desktop|monitor|keyboard|mouse|headset|phone|tablet|other",
  "brand": "string (required)",
  "model": "string (required)",
  "serial_number": "string (unique, optional)",
  "status": "available|assigned|maintenance|retired (default: available)",
  "condition": "new|excellent|good|fair|poor (default: good)",
  "specifications": "JSON object (optional)",
  "purchase_date": "date (optional)",
  "purchase_price": "decimal (optional)",
  "warranty_expiry": "date (optional)",
  "location": "string (optional)",
  "notes": "text (optional)",
  "image": "file (optional)",
  "created_at": "datetime (auto)",
  "updated_at": "datetime (auto)",
  "created_by": "FK to Employee"
}
```

### Assignment Model
```json
{
  "id": "UUID",
  "device": "FK to Device (required)",
  "employee": "FK to Employee (required)",
  "assigned_date": "datetime (auto)",
  "return_date": "datetime (nullable)",
  "expected_return_date": "date (optional)",
  "status": "active|returned|lost|damaged (default: active)",
  "assignment_notes": "text (optional)",
  "return_notes": "text (optional)",
  "assigned_by": "FK to Employee (nullable)"
}
```

### Ticket Request Model
```json
{
  "id": "UUID",
  "ticket_number": "string (unique, auto-generated like TKT001)",
  "requested_by": "FK to Employee (required)",
  "ticket_type": "repair|replacement|new_device|issue|return|other (required)",
  "priority": "low|medium|high|urgent (default: medium)",
  "status": "pending|in_progress|resolved|rejected|closed (default: pending)",
  "device": "FK to Device (nullable)",
  "subject": "string (required)",
  "description": "text (required)",
  "assigned_to": "FK to Employee (nullable)",
  "resolution_notes": "text (optional)",
  "resolved_at": "datetime (nullable)",
  "attachment": "file (optional)",
  "created_at": "datetime (auto)",
  "updated_at": "datetime (auto)"
}
```

---

## Error Handling

### Error Response Format
```json
{
  "error": "Error message",
  "message": "Detailed error message"
}
```

### Common HTTP Status Codes
- `200 OK` - Successful GET, PATCH, PUT request
- `201 Created` - Successful POST request
- `204 No Content` - Successful DELETE request
- `400 Bad Request` - Invalid data or validation error
- `401 Unauthorized` - Missing or invalid token
- `403 Forbidden` - User lacks permission
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

### Validation Errors
```json
{
  "email": ["This field is required", "Enter a valid email address"],
  "password": ["This field is required"],
  "first_name": ["This field is required"]
}
```

---

## Authentication Token Usage

All authenticated requests require an `Authorization` header:

```
Authorization: Bearer {access_token}
```

### Token Expiration
- Access Token: 15 minutes
- Refresh Token: 24 hours

### Refreshing Access Token
When access token expires, make a request to `/api/auth/token/refresh/` with your refresh token to get a new access token.

---

## Deployment Guide

### Backend Deployment (Render.com)

#### 1. Environment Variables
Create a `.env` file with these variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=False

# Database
DATABASE_URL=postgresql://user:password@host:port/dbname

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# AWS S3 (for file uploads)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1

# CORS Settings
ALLOWED_HOSTS=ims-backend-e4fp.onrender.com,localhost
CORS_ALLOWED_ORIGINS=https://ims-frontend-lilac-alpha.vercel.app,http://localhost:5173
```

#### 2. Deployment Steps
1. Connect your GitHub repository to Render
2. Set environment variables in Render dashboard
3. Configure build command: `pip install -r requirements.txt && python manage.py migrate`
4. Configure start command: `gunicorn config.wsgi:application`

#### 3. Run Migrations
```bash
python manage.py migrate
```

#### 4. Create Superuser
```bash
python manage.py createsuperuser # or use the auto-create command
python manage.py create_superuser_auto
```

---

### Frontend Deployment (Vercel)

#### 1. Environment Variables
Create a `.env.local` file:

```env
VITE_API_URL=https://ims-backend-e4fp.onrender.com/api
VITE_APP_NAME=IMS
```

#### 2. Deployment Steps
1. Push code to GitHub
2. Connect repository to Vercel
3. Set environment variables
4. Configure build: `npm run build`
5. Output directory: `dist`

#### 3. Build and Deploy
```bash
npm install
npm run build
```

---

## User Workflows

### 1. Employee Registration & Login
1. User visits signup page
2. Fills form with email, password, name, department
3. System creates employee account
4. Returns JWT tokens (access & refresh)
5. Stores tokens in localStorage
6. Redirects to dashboard

### 2. Request Device Repair/Issue
1. Employee navigates to "Report Issue"
2. Fills ticket form with description, priority, device
3. System creates ticket with status "pending"
4. Admin receives notification
5. Admin assigns ticket and changes status to "in_progress"
6. Admin resolves with resolution notes
7. Employee sees resolved ticket

### 3. Device Assignment Workflow
1. Admin navigates to Assignments
2. Creates new assignment with device & employee
3. Device status changes from "available" to "assigned"
4. Employee sees device in "My Devices"
5. On return, employee clicks "Return Device"
6. Device status changes back to "available"

---

## Testing Credentials

**Admin Account:**
- Email: `admin@company.com`
- Password: Will be generated during setup

**Test Employee Account:**
```json
{
  "email": "test.employee@company.com",
  "password": "TestPassword123!",
  "first_name": "Test",
  "last_name": "Employee",
  "department": "IT"
}
```

---

## Support & Documentation

For issues or questions:
- Check the troubleshooting section
- Review this documentation
- Check server logs on Render dashboard
- Frontend logs in browser console

---

**End of Documentation**
