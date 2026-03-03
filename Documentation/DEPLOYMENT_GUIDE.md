# Deployment Guide - Frontend & Backend

## Table of Contents
1. [Frontend Deployment (Vercel)](#frontend-deployment-vercel)
2. [Backend Deployment (Render.com)](#backend-deployment-rendercom)
3. [Database Setup](#database-setup)
4. [Environment Variables](#environment-variables)
5. [Post-Deployment Testing](#post-deployment-testing)

---

## Frontend Deployment (Vercel)

### Prerequisites
- GitHub account with repository pushed
- Vercel account
- Node.js 16 or higher locally

### Step 1: Connect Repository to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click "Import Project"
3. Select "Import Git Repository"
4. Paste your GitHub repo URL: `https://github.com/VikasChauhanBD/ims-frontend.git`
5. Click "Continue"

### Step 2: Configure Project Settings

```
Framework Preset: Vite
Root Directory: ./ims-frontend
Build Command: npm run build
Output Directory: dist
```

### Step 3: Add Environment Variables

In Vercel Dashboard → Settings → Environment Variables, add:

```env
VITE_API_URL=https://ims-backend-e4fp.onrender.com/api
VITE_APP_NAME=IMS
VITE_APP_VERSION=1.0.0
```

### Step 4: Deploy

1. Click "Deploy"
2. Wait for build to complete
3. Your frontend will be live at: `https://ims-frontend-[vercel-domain].vercel.app`

### Continuous Deployment

Every push to your main branch will automatically deploy!

---

## Backend Deployment (Render.com)

### Prerequisites
- Render account
- PostgreSQL database (can be created on Render)
- GitHub account with backend pushed

### Step 1: Create PostgreSQL Database

1. Go to [render.com](https://render.com)
2. Click "New" → "PostgreSQL"
3. Configure:
   - **Name**: `ims-database`
   - **Database**: `ims_db`
   - **User**: `ims_user`
   - **Plan**: Free (or Starter for production)
4. Click "Create Database"
5. Copy the internal database URL

### Step 2: Deploy Backend Service

1. Click "New" → "Web Service"
2. Connect GitHub repository
3. Configure:

**Name**: `ims-backend`
**Environment**: `Python 3.11`
**Build Command**: 
```bash
pip install -r requirements.txt && python manage.py migrate
```

**Start Command**:
```bash
gunicorn config.wsgi:application
```

### Step 3: Add Environment Variables

In Render Dashboard → Environment, add these variables:

```env
DEBUG=False
SECRET_KEY=your-very-secure-secret-key-change-this
ENVIRONMENT=production
DATABASE_URL=postgresql://ims_user:password@host:port/ims_db
ALLOWED_HOSTS=ims-backend-e4fp.onrender.com,localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=https://ims-frontend-lilac-alpha.vercel.app,http://localhost:5173
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
STATIC_URL=/static/
STATIC_ROOT=/opt/render/project/src/staticfiles
```

### Step 4: Collect Static Files

Add a new command to your `render.yaml`:

```yaml
services:
  - type: web
    name: ims-backend
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --noinput
    startCommand: gunicorn config.wsgi:application
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: ims-database
          property: connectionString
```

### Step 5: Create/Update `render.yaml` in Backend Root

```yaml
version: 0.1

services:
  - type: web
    name: ims-backend
    env: python
    plan: free
    runtime: python-3.11
    buildCommand: >
      pip install -r requirements.txt &&
      python manage.py migrate &&
      python manage.py collectstatic --noinput
    startCommand: gunicorn config.wsgi:application
    healthCheckPath: /api/auth/me/
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: ims-database
          property: connectionString
      - key: PYTHON_VERSION
        value: 3.11.0

databases:
  - name: ims-database
    plan: free
```

### Step 6: Deploy

1. Push `render.yaml` to GitHub
2. Go to Render Dashboard
3. Click "New" → "Web Service"
4. Select GitHub repo
5. Click "Deploy Web Service"

---

## Database Setup

### Initial Migration

After deployment, run:

```bash
python manage.py migrate
```

### Create Superuser

```bash
python manage.py createsuperuser
```

Or use the automatic command:

```bash
python manage.py create_superuser_auto
```

### Default Superuser Credentials
- **Email**: `admin@company.com`
- **Password**: Generated and logged during creation

### Access Admin Panel
```
https://ims-backend-e4fp.onrender.com/admin/
```

---

## Environment Variables

### Backend (.env or .env.production)

```env
# Django Configuration
DEBUG=False
SECRET_KEY=your-secret-key-here-min-50-chars
ENVIRONMENT=production
ALLOWED_HOSTS=ims-backend-e4fp.onrender.com,localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@host:5432/ims_db

# CORS
CORS_ALLOWED_ORIGINS=https://ims-frontend-lilac-alpha.vercel.app,http://localhost:5173
CSRF_TRUSTED_ORIGINS=https://ims-frontend-lilac-alpha.vercel.app,http://localhost:5173

# Email (Optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@ims.com

# JWT
JWT_ACCESS_TOKEN_LIFETIME_MINUTES=15
JWT_REFRESH_TOKEN_LIFETIME_DAYS=7

# AWS S3 (Optional for file uploads)
USE_S3=False
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_STORAGE_BUCKET_NAME=
AWS_S3_REGION_NAME=us-east-1

# Security
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

### Frontend (.env.local)

```env
VITE_API_URL=https://ims-backend-e4fp.onrender.com/api
VITE_APP_NAME=Inventory Management System
VITE_APP_VERSION=1.0.0
VITE_DEBUG=false
```

---

## Post-Deployment Testing

### 1. Test Backend API

```bash
# Test API connectivity
curl https://ims-backend-e4fp.onrender.com/api/auth/me/ \
  -H "Authorization: Bearer {access_token}"

# Test user signup
curl -X POST https://ims-backend-e4fp.onrender.com/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@company.com",
    "password": "TestPass123!",
    "first_name": "Test",
    "last_name": "User",
    "department": "IT"
  }'
```

### 2. Test Frontend Functionality

- [ ] Access login page
- [ ] Create new account
- [ ] Login with account
- [ ] View dashboard
- [ ] View devices
- [ ] Create repair ticket
- [ ] Create issue report
- [ ] View my tickets
- [ ] Logout

### 3. Check Server Logs

**Render Backend Logs**:
```
Dashboard → Select Service → Logs
```

**Vercel Frontend Logs**:
```
Dashboard → Select Project → Deployments → Logs
```

### 4. Common Issues & Solutions

#### Issue: CORS Error
**Solution**: Check `CORS_ALLOWED_ORIGINS` in backend settings

#### Issue: 404 on API Endpoints
**Solution**: Verify `ALLOWED_HOSTS` includes your domain

#### Issue: Database Connection Error
**Solution**: Verify `DATABASE_URL` is correct in environment variables

#### Issue: Static Files Not Loading
**Solution**: Run `collectstatic` command on backend

---

## Performance Optimization

### Frontend
- Enable Gzip compression in Vercel
- Optimize images
- Code splitting for lazy loading
- Minify CSS/JS

### Backend
- Use database query optimization
- Enable caching
- Use CDN for static files (AWS CloudFront)
- Monitor endpoint performance

---

## Monitoring & Maintenance

### Backend Monitoring
1. Check Render dashboard for error logs
2. Monitor database usage
3. Review API response times

### Frontend Monitoring
1. Check Vercel Analytics
2. Monitor page load times
3. Track deployment status

### Regular Maintenance
- Update dependencies monthly
- Review and rotate secret keys
- Clean up old logs
- Backup database weekly

---

## Rollback Procedures

### Frontend Rollback (Vercel)
1. Go to Deployments tab
2. Click on previous deployment
3. Click "Redeploy"

### Backend Rollback (Render)
1. Go to Render Dashboard
2. Select service
3. Click "Previous Deployments"
4. Click "Redeploy" on desired version

---

## Custom Domain Setup

### Frontend Custom Domain
1. Vercel Dashboard → Settings → Domains
2. Add your domain
3. Follow DNS configuration instructions

### Backend Custom Domain
1. Render Dashboard → Environment → Custom Domain
2. Add your domain
3. Update DNS records as instructed

---

## Final Checklist

- [ ] Backend deployed and running
- [ ] Database migrations complete
- [ ] Frontend deployed and accessible
- [ ] API connectivity tested
- [ ] All user workflows tested
- [ ] SSL/HTTPS working
- [ ] Email notifications configured (if needed)
- [ ] Monitoring set up
- [ ] Backups configured
- [ ] Documentation updated

---

**Deployment Complete!** 🎉

Your IMS is now live and ready for use.
