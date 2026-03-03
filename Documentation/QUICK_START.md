# IMS Quick Start Guide

## Overview
Complete Inventory Management System ready for deployment. All backend APIs are working, frontend is integrated with real data.

## What's Included

✅ **Backend (Django REST)**
- User authentication & authorization
- Device management
- Device assignments
- Ticket/Issue management
- Dashboard statistics
- Role-based access control

✅ **Frontend (React + Vite)**
- User registration & login
- Device browsing
- My devices view
- Raise repair tickets
- Report issues
- View ticket status
- Responsive design

✅ **Documentation**
- API_DOCUMENTATION.md - Complete API reference
- DEPLOYMENT_GUIDE.md - Step by step deployment
- INTEGRATION_GUIDE.md - Full system architecture

---

## Quick Start (Development)

### 1. Backend Setup (5 minutes)

```bash
cd ims-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env

# Run migrations
python manage.py migrate

# Create admin account
python manage.py createsuperuser

# Start server
python manage.py runserver
# Backend: http://localhost:8000
```

### 2. Frontend Setup (3 minutes)

```bash
cd ims-backend/ims-frontend

# Install dependencies
npm install

# Setup environment
cp .env.example .env.local
# Edit .env.local - set VITE_API_URL=http://localhost:8000/api

# Start dev server
npm run dev
# Frontend: http://localhost:5173
```

### 3. Test the Application

```
URL: http://localhost:5173
1. Click "Create Account"
2. Fill signup form
3. Login with created account
4. Explore dashboard
5. Create a repair ticket
6. View all features
```

---

## User Workflows

### Employee Flow
1. **Register** → Sign up with email, password, name, department
2. **Login** → Access dashboard
3. **View Devices** → See all available devices
4. **My Devices** → See devices assigned to me
5. **Report Issue** → Create a new issue ticket
6. **Raise Repair Ticket** → Request device repair
7. **Check Status** → View ticket status
8. **Return Device** → Return assigned device

### Admin Flow (Backend Only - UI Coming Soon)
1. **Create Devices** → Add inventory items
2. **Manage Assignments** → Assign devices to employees
3. **View Tickets** → See all support tickets
4. **Assign Ticket** → Assign to technician
5. **Resolve Ticket** → Mark as complete

---

## API Endpoints (Key)

### Auth
```
POST   /api/auth/signup/
POST   /api/auth/login/
POST   /api/auth/logout/
GET    /api/auth/me/
PATCH  /api/auth/me/
```

### Devices
```
GET    /api/inventory/devices/
POST   /api/inventory/devices/
GET    /api/inventory/devices/{id}/
PATCH  /api/inventory/devices/{id}/
```

### Assignments
```
GET    /api/inventory/assignments/
POST   /api/inventory/assignments/
POST   /api/inventory/assignments/{id}/return_device/
GET    /api/inventory/assignments/my_assignments/
```

### Tickets
```
GET    /api/inventory/tickets/
POST   /api/inventory/tickets/
POST   /api/inventory/tickets/{id}/assign/
POST   /api/inventory/tickets/{id}/resolve/
GET    /api/inventory/tickets/my_tickets/
```

---

## Deployment (2 steps)

### Step 1: Deploy Backend (Render)
1. Go to render.com
2. Connect GitHub repo
3. Set environment variables (see DEPLOYMENT_GUIDE.md)
4. Deploy

### Step 2: Deploy Frontend (Vercel)
1. Go to vercel.com
2. Connect GitHub repo (ims-frontend)
3. Set `VITE_API_URL` to your Render backend URL
4. Deploy

---

## Features Implemented

### ✅ Complete
- User authentication (signup, login, logout, password reset)
- Device listing and filtering
- Device assignment management
- Ticket creation and tracking
- Issue reporting
- Real-time API integration
- Responsive UI
- Error handling
- JWT token management

### 🚧 Partial
- Admin dashboard (backend API ready, UI coming)
- File uploads (backend ready, not fully tested)

### 📋 Future
- Email notifications
- Advanced analytics
- Mobile app
- Desktop notifications
- Audit logs

---

## Component Status

### Frontend Components

| Component | Status | Notes |
|-----------|--------|-------|
| Login | ✅ Complete | Working with backend |
| Signup | ✅ Complete | Integrated with API |
| Navbar | ✅ Complete | Role-aware |
| User Dashboard | ✅ Complete | Loads real data |
| Devices View | ✅ Complete | Lists all devices |
| My Devices | ✅ Complete | Shows assignments |
| Repair Ticket | ✅ Complete | Creates tickets |
| Report Issue | ⚠️ Partial | Uses same as repair |
| Admin Dashboard | ❌ Not Started | API ready |
| Device Management | ⚠️ Partial | Backend ready |
| Profile | ⚠️ Partial | Backend ready |

---

## Data Models (Backend)

### Employee
- UUID id
- Email (unique)
- First/Last name
- Role (admin/manager/employee)
- Department
- Phone number
- Timestamps

### Device
- UUID id
- Device ID (unique)
- Name, brand, model
- Type (laptop, desktop, monitor, etc)
- Status (available, assigned, maintenance, retired)
- Condition (new, excellent, good, fair, poor)
- Purchase info, warranty
- Location, notes

### Assignment
- UUID id
- Device FK
- Employee FK
- Status (active, returned, lost, damaged)
- Assigned date, return date
- Expected return date

### Ticket
- UUID id
- Auto-generated ticket number (TKT001, TKT002, etc)
- Type (repair, replacement, issue, etc)
- Priority (low, medium, high, urgent)
- Status (pending, in_progress, resolved, rejected, closed)
- Subject, description
- Device FK (optional)
- Assigned to FK
- Resolution notes

---

## Environment Variables

### Backend (.env)
```
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@host/dbname
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

### Frontend (.env.local)
```
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=IMS
```

---

## Troubleshooting

### Errors to Check

**ModuleNotFoundError in Python**
```
Solution: pip install -r requirements.txt
```

**CORS Error in Browser**
```
Solution: Check CORS_ALLOWED_ORIGINS in backend .env
```

**API 404 Errors**
```
Solution: Verify backend is running on correct port
```

**npm: command not found**
```
Solution: Install Node.js from nodejs.org
```

### Debug Commands

```bash
# Backend
python manage.py runserver --verbose  # Detailed logging
python manage.py shell                # Django shell
python manage.py migrate --plan       # Show migration plan

# Frontend
npm run build                         # Build for production
npm run preview                       # Preview build locally
```

---

## Next Steps

1. **Review Documentation**
   - Read INTEGRATION_GUIDE.md for system overview
   - Read API_DOCUMENTATION.md for endpoint reference

2. **Deploy to Production**
   - Follow DEPLOYMENT_GUIDE.md
   - Deploy backend to Render
   - Deploy frontend to Vercel

3. **Complete Admin Features**
   - Implement admin dashboard UI
   - Add device management pages
   - Add assignment management

4. **Add Missing Features**
   - Implement remaining TODO components
   - Add email notifications
   - Add file upload support

5. **Test Everything**
   - Test all user workflows
   - Test all API endpoints
   - Test error handling
   - Load testing

---

## File Structure

```
ims-backend/
├── API_DOCUMENTATION.md          ← Read this for API ref
├── DEPLOYMENT_GUIDE.md           ← Read this for deployment
├── INTEGRATION_GUIDE.md          ← Read this for architecture
├── README.md (this file)          ← You are here
├── .env.example                  ← Copy to .env
├── requirements.txt              ← Python dependencies
├── manage.py                     ← Django CLI
├── Procfile                      ← Deployment config
├── render.yaml                   ← Render config
├── config/                       ← Django settings
├── apps/
│   ├── authentication/           ← Auth system
│   └── inventory/                ← Main features
└── ims-frontend/
    ├── package.json              ← Node dependencies
    ├── .env.example              ← Copy to .env.local
    ├── vite.config.js            ← Vite config
    ├── index.html                ← Entry HTML
    └── src/
        ├── services/api.js       ← API client
        ├── pages/                ← Page components
        ├── components/           ← UI components
        └── AuthContext/          ← Auth state
```

---

## Key Files to Review

1. **API_DOCUMENTATION.md** - Complete API reference (all endpoints)
2. **DEPLOYMENT_GUIDE.md** - How to deploy to production
3. **INTEGRATION_GUIDE.md** - System architecture and workflows
4. **backend/apps/authentication/views.py** - Auth endpoints
5. **backend/apps/inventory/views.py** - Device/Ticket endpoints
6. **frontend/src/services/api.js** - API client setup
7. **frontend/src/AuthContext/AuthContext.jsx** - Auth state

---

## Support

- **Documentation**: See API_DOCUMENTATION.md and DEPLOYMENT_GUIDE.md
- **Architecture**: See INTEGRATION_GUIDE.md
- **Development**: Check each module's README or docstrings
- **Issues**: Check server logs: `python manage.py runserver`

---

## Quick Commands

```bash
# Backend dev
python manage.py runserver

# Backend admin
python manage.py createsuperuser
python manage.py migrate
python manage.py collectstatic

# Frontend dev
npm run dev

# Frontend build
npm run build

# Test
python manage.py test
npm run test
```

---

**Ready to get started!** 🚀

Start with `npm run dev` in ims-frontend and `python manage.py runserver` in ims-backend.

