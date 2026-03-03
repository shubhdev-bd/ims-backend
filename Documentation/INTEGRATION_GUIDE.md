# Inventory Management System (IMS) - Complete Integration Guide

**Version:** 1.0.0  
**Last Updated:** March 2, 2026  
**Status:** Ready for Deployment

---

## Executive Summary

The Inventory Management System is a full-stack web application for managing company inventory and device assignments. The system includes:

- **Backend**: Django REST API with PostgreSQL database
- **Frontend**: React with Vite
- **Authentication**: JWT-based with role-based access control
- **Features**: Device tracking, assignments, ticket management, issue reporting

---

## System Architecture

```
┌─────────────────────────────────────────────┐
│          Frontend (Vercel)                   │
│     React + Vite + Tailwind CSS             │
│  https://ims-frontend.vercel.app            │
└──────────────┬──────────────────────────────┘
               │ HTTPS / REST API
               ↓
┌─────────────────────────────────────────────┐
│          Backend (Render)                    │
│     Django REST Framework                    │
│  https://ims-backend.onrender.com/api       │
└──────────────┬──────────────────────────────┘
               │ SQL Queries
               ↓
┌─────────────────────────────────────────────┐
│        PostgreSQL Database                   │
│          (Render)                            │
└─────────────────────────────────────────────┘
```

---

## Directory Structure

### Backend (`/ims-backend`)

```
ims-backend/
├── manage.py                          # Django management script
├── requirements.txt                   # Python dependencies
├── runtime.txt                        # Python version
├── Procfile                          # Heroku/Render deployment config
├── render.yaml                       # Render deployment config
├── .env.example                      # Environment variables template
├── API_DOCUMENTATION.md              # Full API documentation
├── DEPLOYMENT_GUIDE.md               # Deployment instructions
│
├── config/                           # Django project settings
│   ├── settings.py                   # Main Django settings
│   ├── urls.py                       # URL routing
│   ├── asgi.py                       # ASGI config (async)
│   └── wsgi.py                       # WSGI config (production)
│
└── apps/
    ├── authentication/               # User auth & profiles
    │   ├── models.py                 # Employee model
    │   ├── views.py                  # Auth endpoints
    │   ├── serializers.py            # Data serialization
    │   ├── urls.py                   # Auth routes
    │   └── utils.py                  # Utility functions
    │
    └── inventory/                    # Device & ticket management
        ├── models.py                 # Device, Assignment, Ticket models
        ├── views.py                  # Inventory endpoints
        ├── serializers.py            # Data serialization
        ├── permissions.py            # Custom permissions
        └── urls.py                   # Inventory routes
```

### Frontend (`/ims-backend/ims-frontend`)

```
ims-frontend/
├── package.json                      # Node dependencies
├── vite.config.js                    # Vite configuration
├── .env.example                      # Environment variables template
├── .env.local                        # Local environment (git-ignored)
│
├── index.html                        # HTML entry point
├── src/
│   ├── main.jsx                      # React entry point
│   ├── App.jsx                       # Root component
│   ├── App.css                       # Global styles
│   │
│   ├── services/
│   │   └── api.js                    # API client & endpoints
│   │
│   ├── AuthContext/
│   │   └── AuthContext.jsx           # Auth state management
│   │
│   ├── pages/                        # Page components
│   │   ├── loginPage/                # Login page
│   │   ├── signupPage/               # Registration page
│   │   ├── userPage/                 # User dashboard
│   │   ├── adminPage/                # Admin dashboard (TODO)
│   │   ├── forgetpasswordPage/       # Password reset
│   │   └── resetPasswordPage/        # Password reset confirm
│   │
│   ├── components/
│   │   ├── navbar/                   # Navigation component
│   │   ├── animatedBackground/       # Animated BG effect
│   │   ├── user/                     # User-specific components
│   │   │   ├── myDevices/            # Assigned devices list
│   │   │   ├── userDevices/          # All devices view
│   │   │   ├── myTickets/            # User's tickets
│   │   │   ├── raiseRepairTicket/    # Create repair ticket
│   │   │   ├── reportIssue/          # Report issue
│   │   │   ├── requestHistory/       # Request history (TODO)
│   │   │   ├── overDueItems/         # Overdue devices (TODO)
│   │   │   ├── activityLog/          # Activity log (TODO)
│   │   │   └── profile/              # User profile
│   │   │
│   │   └── admin/                    # Admin-specific components
│   │       ├── dashboard/            # Admin dashboard (TODO)
│   │       ├── devices/              # Device management
│   │       ├── employees/            # Employee management
│   │       ├── assignments/          # Assignment management
│   │       ├── ticketRequestsView/   # Ticket management
│   │       └── profile/              # Admin profile
│   │
│   └── assets/
│       ├── data/
│       │   ├── mockData.js           # DEPRECATED - Remove
│       │   └── types.js              # Type definitions
│       └── images/                   # Image assets
```

---

## Key Features

### 1. Authentication & Authorization
- **Sign Up**: New employee registration
- **Login**: JWT token authentication
- **Password Reset**: Email-based password recovery
- **Role-Based Access**: Admin, Manager, Employee roles

### 2. Device Management
- **View Devices**: See all inventory devices
- **Device Details**: Specifications, purchase info, warranty
- **Device Status**: Available, Assigned, Maintenance, Retired
- **Device Assignment**: Assign devices to employees

### 3. Device Assignment
- **Create Assignment**: Allocate device to employee
- **Return Device**: Employee returns assigned device
- **Assignment History**: Track all assignments
- **Overdue Returns**: Monitor devices past return date

### 4. Ticket Management
- **Create Ticket**: Report issues or request repairs
- **Ticket Types**: Repair, Replacement, New Device, Issue, Return
- **Priority Levels**: Low, Medium, High, Urgent
- **Ticket Tracking**: Monitor status from pending to resolved
- **Admin Resolution**: Assign, update status, add resolution notes

### 5. Dashboard
- **Statistics**: Device counts, assignment status, ticket metrics
- **Quick Actions**: Fast access to common tasks
- **Recent Items**: Last tickets and assignments

---

## API Endpoints Summary

### Authentication
```
POST   /api/auth/signup/              - Register new account
POST   /api/auth/login/               - Login
POST   /api/auth/logout/              - Logout
POST   /api/auth/token/refresh/       - Refresh JWT token
GET    /api/auth/me/                  - Get current user profile
PATCH  /api/auth/me/                  - Update profile
POST   /api/auth/password/change/     - Change password
POST   /api/auth/password/reset/      - Request password reset
POST   /api/auth/password/reset/confirm/ - Reset password
```

### Devices
```
GET    /api/inventory/devices/                     - List all devices
POST   /api/inventory/devices/                     - Create device (admin only)
GET    /api/inventory/devices/{id}/                - Get device details
PATCH  /api/inventory/devices/{id}/                - Update device
DELETE /api/inventory/devices/{id}/                - Delete device
GET    /api/inventory/devices/available/           - Get available devices
POST   /api/inventory/devices/{id}/mark_maintenance/ - Mark as maintenance
POST   /api/inventory/devices/{id}/mark_available/   - Mark as available
```

### Assignments
```
GET    /api/inventory/assignments/                 - List assignments
POST   /api/inventory/assignments/                 - Create assignment
GET    /api/inventory/assignments/{id}/            - Get assignment
PATCH  /api/inventory/assignments/{id}/            - Update assignment
DELETE /api/inventory/assignments/{id}/            - Delete assignment
POST   /api/inventory/assignments/{id}/return_device/ - Return device
GET    /api/inventory/assignments/my_assignments/   - User's assignments
```

### Tickets
```
GET    /api/inventory/tickets/                    - List tickets
POST   /api/inventory/tickets/                    - Create ticket
GET    /api/inventory/tickets/{id}/               - Get ticket details
PATCH  /api/inventory/tickets/{id}/               - Update ticket
DELETE /api/inventory/tickets/{id}/               - Delete ticket
POST   /api/inventory/tickets/{id}/assign/        - Assign ticket
POST   /api/inventory/tickets/{id}/resolve/       - Resolve ticket
GET    /api/inventory/tickets/my_tickets/         - User's tickets
```

### Dashboard
```
GET    /api/inventory/dashboard/stats/            - Get dashboard statistics
```

---

## User Workflows

### Workflow 1: Employee Registration to Getting Device

**Step 1: Sign Up**
```
1. Visit login page
2. Click "Create Account"
3. Fill form: email, password, name, department, phone
4. Click "Create Account"
5. System creates account and logs in automatically
6. Redirected to dashboard
```

**API Calls**:
- `POST /api/auth/signup/`

**Step 2: View Available Devices**
```
1. Click "Devices" tab
2. See list of all available devices
3. Click device to see details
```

**API Calls**:
- `GET /api/inventory/devices/`
- `GET /api/inventory/devices/{id}/`

**Step 3: Receive Device Assignment**
```
1. Admin visits admin dashboard (future feature)
2. Creates assignment for employee & device
3. Employee sees device in "My Devices" tab
```

**API Calls** (Admin):
- `POST /api/inventory/assignments/`

**API Calls** (User):
- `GET /api/inventory/assignments/my_assignments/`

---

### Workflow 2: Report Issue or Request Repair

**Step 1: Create Ticket**
```
1. Employee clicks "Report Issue" or "Repair Ticket"
2. Selects ticket type and priority
3. Selects device (if applicable)
4. Enters subject and description
5. Optionally uploads image
6. Clicks "Submit Ticket"
```

**API Call**:
- `POST /api/inventory/tickets/`

**Step 2: Admin Reviews Ticket**
```
1. Admin sees new pending ticket
2. Can assign to technician
3. Updates status to "in_progress"
```

**API Calls** (Admin):
- `POST /api/inventory/tickets/{id}/assign/`
- `PATCH /api/inventory/tickets/{id}/`

**Step 3: Ticket Resolution**
```
1. Technician completes repair
2. Admin adds resolution notes
3. Changes status to "resolved"
4. Employee sees updated status
```

**API Call** (Admin):
- `POST /api/inventory/tickets/{id}/resolve/`

---

### Workflow 3: Return Device

**Step 1: Employee Initiates Return**
```
1. Navigate to "My Devices"
2. Click "Return Device"
3. Optionally add return notes
4. Click "Confirm Return"
```

**API Call**:
- `POST /api/inventory/assignments/{id}/return_device/`

**Step 2: Device Marked Available**
```
1. System updates assignment status to "returned"
2. Device status changes to "available"
3. Assignment removed from "My Devices"
```

---

## Data Models

### Employee
- Unique email
- First and last name
- Employee ID
- Role (Admin, Manager, Employee)
- Department (IT, HR, Finance, Operations, Sales, Marketing)
- Phone number
- Profile picture
- Status (Active/Inactive)
- Timestamps

### Device
- Unique device ID
- Name and model details
- Type (Laptop, Desktop, Monitor, Keyboard, Mouse, Headset, Phone, Tablet, Other)
- Brand
- Serial number
- Status (Available, Assigned, Maintenance, Retired)
- Condition (New, Excellent, Good, Fair, Poor)
- Specifications (JSON)
- Purchase information (date, price, warranty)
- Location
- Notes and image

### Assignment
- Device reference
- Employee reference
- Status (Active, Returned, Lost, Damaged)
- Assigned date and expected return date
- Return date and notes
- Assigned by (Manager/Admin)

### Ticket Request
- Auto-generated ticket number
- Type (Repair, Replacement, New Device, Issue, Return, Other)
- Priority (Low, Medium, High, Urgent)
- Status (Pending, In Progress, Resolved, Rejected, Closed)
- Subject and description
- Device reference (if applicable)
- Assigned to (Manager/Admin)
- Resolution notes and date
- Attachment/image
- Timestamps

---

## Technology Stack

### Backend
- **Framework**: Django 4.2+
- **API**: Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: Simple JWT
- **Server**: Gunicorn (production)
- **Deployment**: Render.com
- **ORM**: Django ORM

### Frontend
- **Framework**: React 18+
- **Build Tool**: Vite
- **Styling**: CSS + Responsive Design
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **State Management**: Context API
- **Deployment**: Vercel

### DevOps
- **VCS**: GitHub
- **Database**: PostgreSQL (Render)
- **Hosting**: Render (Backend), Vercel (Frontend)
- **HTTPS**: Automatic SSL

---

## Development Setup

### Backend Setup

```bash
# Clone repository
git clone https://github.com/VikasChauhanBD/ims-backend.git
cd ims-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
# Edit .env with your settings

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
# Server runs on http://localhost:8000
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd ims-frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env.local
# Edit .env.local with your API URL

# Run development server
npm run dev
# Frontend runs on http://localhost:5173
```

---

## Testing Checklist

### Authentication
- [ ] Sign up new account
- [ ] Login with account
- [ ] Logout
- [ ] Password reset flow
- [ ] Token refresh

### Devices
- [ ] View all devices
- [ ] Filter devices by status
- [ ] View device details
- [ ] Admin: Create device
- [ ] Admin: Update device
- [ ] Admin: Delete device

### Assignments
- [ ] User: View my devices
- [ ] Admin: Create assignment
- [ ] User: Return device
- [ ] View assignment history

### Tickets
- [ ] User: Create repair ticket
- [ ] User: Create issue report
- [ ] User: View my tickets
- [ ] Admin: View all tickets
- [ ] Admin: Assign ticket
- [ ] Admin: Resolve ticket

### Dashboard
- [ ] View statistics
- [ ] See recent activities
- [ ] Quick action buttons

---

## Known Limitations & Future Features

### Current Limitations
- Admin dashboard UI not fully implemented (backend ready)
- File uploads not configured (backend ready)
- Email notifications not configured (backend ready)
- No bulk operations (import/export)

### Future Features
- [ ] Bulk device import from CSV
- [ ] Advanced reporting & analytics
- [ ] Mobile app
- [ ] Audit logs
- [ ] Device condition tracking photos
- [ ] Maintenance schedules
- [ ] Asset depreciation tracking
- [ ] Multi-language support
- [ ] Two-factor authentication
- [ ] API rate limiting

---

## Troubleshooting

### Frontend Issues

**Issue: API requests failing with 401**
- Ensure tokens are being stored in localStorage
- Check if token is expired
- Try logging in again

**Issue: CORS errors**
- Verify `VITE_API_URL` is correct in `.env.local`
- Check backend `CORS_ALLOWED_ORIGINS`

**Issue: Blank page on load**
- Check browser console for errors
- Verify API connectivity
- Check if backend is running

### Backend Issues

**Issue: Database connection error**
- Verify `DATABASE_URL` in `.env`
- Ensure database service is running
- Check database credentials

**Issue: 500 errors on API requests**
- Check server logs: `python manage.py runserver`
- Verify all dependencies are installed
- Run migrations: `python manage.py migrate`

**Issue: Static files not loading**
- Run: `python manage.py collectstatic`
- Check `STATIC_URL` and `STATIC_ROOT` settings

---

## Performance Tips

### Frontend
- Use React DevTools to profile components
- Check Network tab for slow API calls
- Lazy load routes and components
- Optimize images

### Backend
- Use Django Debug Toolbar in development
- Profile slow queries with Django Silk
- Enable caching for frequently accessed data
- Use database indexes

---

## Security Best Practices

1. **Never commit `.env` files** - Use `.env.example`
2. **Use strong SECRET_KEY** - Min 50 random characters
3. **Enable HTTPS** - Automatic on Vercel and Render
4. **Protect sensitive endpoints** - Use authentication
5. **Validate all inputs** - Backend validation is critical
6. **Use environment variables** - Never hardcode credentials
7. **Keep dependencies updated** - Run `pip freeze` and `npm audit`
8. **Use HTTPS for API calls** - Always in production

---

## Support & Resources

### Documentation
- [API Documentation](./API_DOCUMENTATION.md)
- [Deployment Guide](./DEPLOYMENT_GUIDE.md)
- [Django Docs](https://docs.djangoproject.com/)
- [React Docs](https://react.dev/)
- [DRF Docs](https://www.django-rest-framework.org/)

### Community
- Django Community: https://www.djangoproject.com/community/
- React Community: https://react.dev/community
- Stack Overflow: Tag `django`, `react`, `django-rest-framework`

---

## Contact & Support

For issues or questions:
1. Check the documentation
2. Review error messages in logs
3. Search Stack Overflow
4. Create GitHub issue

---

**Last Updated**: March 2, 2026  
**Version**: 1.0.0  
**Status**: Production Ready

