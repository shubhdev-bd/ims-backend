# Inventory Management System (IMS)

A comprehensive full-stack web application for managing company inventory, device assignments, and support tickets.

![Status](https://img.shields.io/badge/status-production%20ready-brightgreen)
![Version](https://img.shields.io/badge/version-1.0.0-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 📋 Quick Links

| Document | Purpose |
|----------|---------|
| [QUICK_START.md](./QUICK_START.md) | ⚡ Get running in 10 minutes |
| [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) | 📚 Complete API reference |
| [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) | 🚀 Deploy to production |
| [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) | 🏗️ System architecture & workflows |

---

## 🎯 Features

### ✅ Implemented
- **User Management**: Registration, login, profiles, password reset
- **Device Inventory**: Track all company devices with detailed specs
- **Device Assignment**: Assign/return devices to employees
- **Ticket System**: Create and track repair/issue tickets
- **Dashboard**: Real-time statistics and quick actions
- **Role-Based Access**: Admin, Manager, Employee roles
- **JWT Authentication**: Secure token-based auth
- **Real-time API**: All data synced with backend

### 🚧 In Progress
- Admin dashboard UI
- Advanced filtering and search

### 📋 Coming Soon
- Email notifications
- File attachment upload
- Mobile app
- Analytics and reporting

---

## 🏗️ System Architecture

```
Frontend (Vercel)           Backend (Render)          Database
React + Vite         →      Django REST API    →     PostgreSQL
localhost:5173              localhost:8000            
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 14+
- Git

### Backend (5 minutes)

```bash
cd ims-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py runserver
# API: http://localhost:8000/api
```

### Frontend (3 minutes)

```bash
cd ims-backend/ims-frontend
npm install
cp .env.example .env.local
# Edit .env.local: VITE_API_URL=http://localhost:8000/api
npm run dev
# App: http://localhost:5173
```

### Test Account
```
Email: admin@company.com
Password: (created during setup)
```

---

## 📚 Documentation

### Getting Started
- **New to the project?** → Read [QUICK_START.md](./QUICK_START.md)
- **Want to understand the system?** → Read [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)

### Development
- **API endpoints?** → Check [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
- **How to deploy?** → Follow [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)

### API Reference
See [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for:
- All endpoints
- Request/response examples
- Error handling
- Data models

---

## 🛠️ Technology Stack

### Backend
```
Django 4.2          REST Framework
PostgreSQL          Simple JWT
Gunicorn            CORS Headers
Python 3.11         Django Extensions
```

### Frontend
```
React 18            Vite
Tailwind CSS        Axios
Lucide Icons        Context API
Responsive Design
```

### DevOps
```
GitHub              Render (Backend)
Vercel (Frontend)   PostgreSQL (Render)
```

---

## 📱 Key Pages & Components

### User Pages
```
/login              - User login
/signup             - User registration
/dashboard          - User dashboard
/devices            - All devices
/mydevices          - Assigned devices
/raiserepairticket  - Create repair ticket
/reportissue        - Report issue
/tickets            - My tickets
```

### Admin Pages (Backend ready, UI TBD)
```
/admin/devices      - Device management
/admin/assignments  - Assignment management
/admin/tickets      - Ticket management
/admin/employees    - Employee management
```

---

## 🔌 API Endpoints (Sample)

```bash
# Authentication
POST   /api/auth/signup/
POST   /api/auth/login/
GET    /api/auth/me/

# Devices
GET    /api/inventory/devices/
POST   /api/inventory/devices/

# Tickets
POST   /api/inventory/tickets/
GET    /api/inventory/tickets/my_tickets/

# Complete reference: See API_DOCUMENTATION.md
```

---

## 🔐 Environment Variables

### Backend (.env)
```env
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@host/dbname
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

### Frontend (.env.local)
```env
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=IMS
```

See `.env.example` files for complete options.

---

## 📦 Project Structure

```
ims-backend/                 # Backend Django project
├── config/                  # Django settings
├── apps/
│   ├── authentication/      # User auth & profiles
│   └── inventory/           # Devices, assignments, tickets
├── API_DOCUMENTATION.md     # API reference
├── DEPLOYMENT_GUIDE.md      # Deployment instructions
├── INTEGRATION_GUIDE.md     # Architecture & workflows
└── QUICK_START.md           # Quick start guide

ims-frontend/                # Frontend React app
├── src/
│   ├── pages/               # Page components
│   ├── components/          # UI components
│   ├── services/api.js      # API client
│   └── AuthContext/         # Auth state
├── vite.config.js           # Vite configuration
└── package.json             # Dependencies
```

---

## 🧪 Testing

### Backend Tests
```bash
python manage.py test
```

### Frontend Tests
```bash
npm test
```

---

## 🚢 Deployment

### Deploy Backend (Render)
```bash
1. Push to GitHub
2. Create service on Render
3. Set environment variables
4. Deploy
```

### Deploy Frontend (Vercel)
```bash
1. Push to GitHub
2. Import project to Vercel
3. Set VITE_API_URL
4. Deploy
```

See [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md) for detailed steps.

---

## 🐛 Troubleshooting

### Backend Issues
- **Database error**: Check `DATABASE_URL` in .env
- **CORS error**: Verify `CORS_ALLOWED_ORIGINS`
- **500 error**: Check `python manage.py runserver` logs
- **Static files**: Run `python manage.py collectstatic`

### Frontend Issues
- **API 401**: User not authenticated, login again
- **API 404**: Verify backend URL in .env.local
- **Blank page**: Check browser console for errors
- **CORS error**: Backend misconfigured

### Common Solutions
```bash
# Reset database
python manage.py migrate

# Create new admin
python manage.py createsuperuser

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
npm install --force

# Clear cache
rm -rf ~/.cache/pip
npm cache clean --force
```

---

## 📝 User Workflows

### Employee Registration to Using System
1. Visit application
2. Click "Create Account"
3. Fill signup form (email, password, name, department)
4. System logs in automatically
5. Browse devices
6. Submit repair/issue tickets
7. Track ticket status
8. Return devices when done

### Admin Workflow (Backend Ready)
1. Create devices in inventory
2. Create device assignments
3. Review and assign tickets
4. Resolve tickets with notes

---

## 🤝 Contributing

Guidelines:
1. Create feature branch: `git checkout -b feature/name`
2. Make changes and commit
3. Push to GitHub
4. Create Pull Request

---

## 📄 License

MIT License - See LICENSE file for details

---

## 📞 Support

### Documentation
- **Quick Start**: [QUICK_START.md](./QUICK_START.md)
- **API Docs**: [API_DOCUMENTATION.md](./API_DOCUMENTATION.md)
- **Deploy**: [DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)
- **Architecture**: [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md)

### Getting Help
1. Check documentation files
2. Review error messages carefully
3. Check server logs
4. Search documentation for keywords

---

## 🗺️ Roadmap

### v1.0 (Current)
- ✅ Core functionality
- ✅ User authentication
- ✅ Device tracking
- ✅ Ticket management

### v1.1 (Next)
- 📋 Admin dashboard UI
- 📋 Email notifications
- 📋 File uploads
- 📋 Advanced reporting

### v2.0 (Future)
- 📋 Mobile app
- 📋 Analytics dashboard
- 📋 API rate limiting
- 📋 Audit logs

---

## 🎓 Learning Resources

- [Django Documentation](https://docs.djangoproject.com/)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [React Documentation](https://react.dev/)
- [Vite Documentation](https://vitejs.dev/)

---

## 📊 Stats

- **Backend**: ~2000 lines of Python
- **Frontend**: ~3000 lines of JavaScript/JSX
- **Documentation**: 4 comprehensive guides
- **API Endpoints**: 25+ endpoints
- **Database Models**: 4 main models
- **Frontend Pages**: 7 main pages

---

## 🙏 Acknowledgments

Built with modern web technologies and best practices.

---

## 📅 Version History

### v1.0.0 (March 2, 2026)
- Initial release
- All core features implemented
- Full API documentation
- Production ready

---

**Status**: ✅ Production Ready

**Last Updated**: March 2, 2026

**Maintained by**: [Your Team]

---

## Quick Commands Reference

```bash
# Backend
python manage.py runserver              # Start dev server
python manage.py migrate                # Run migrations
python manage.py createsuperuser        # Create admin
python manage.py collectstatic          # Collect static files

# Frontend
npm run dev                             # Start dev server
npm run build                           # Build for production
npm run preview                         # Preview build
npm run lint                            # Lint code

# Both
git push origin main                    # Deploy to production
```

---

**Ready to get started?** → Read [QUICK_START.md](./QUICK_START.md) 🚀
