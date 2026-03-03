# Testing Guide - Complete Flow

## Prerequisites
- Backend running on `http://localhost:8000`
- Frontend running on `http://localhost:5173`
- Fresh database or test data loaded

## Test Flows

### 1. User Registration & Login Flow

#### Test Case 1.1: New User Signup
```
Steps:
1. Navigate to http://localhost:5173
2. Click "Create Account"
3. Fill in form:
   - Email: testuser@example.com
   - First Name: John
   - Last Name: Doe
   - Department: IT
   - Password: TestPassword123!
   - Confirm: TestPassword123!
4. Click "Create Account"

Expected Results:
✓ Account created successfully
✓ Automatically logged in
✓ Redirected to user dashboard (/devices)
✓ User role is 'employee'
```

#### Test Case 1.2: Admin User Signup
```
Steps:
1. Use Django admin or database to create admin user:
   python manage.py createsuperuser
   Email: admin@example.com
   Password: AdminPassword123!
   Role: admin

2. Go to http://localhost:5173/login
3. Login with admin credentials

Expected Results:
✓ Login successful
✓ Automatically redirected to /admin/dashboard (NOT /dashboard)
✓ Admin panel visible with all tabs: Dashboard, Devices, Employees, Assignments, Ticket Requests
```

#### Test Case 1.3: User Login & Logout
```
Steps:
1. Logout (if logged in)
2. Click "Sign In"
3. Enter testuser@example.com / TestPassword123!
4. Click "Sign In"
5. Once logged in, click profile/logout button

Expected Results:
✓ Login successful
✓ Redirected to /devices page
✓ Current user data loaded and visible
✓ Logout clears tokens and redirects to login
```

---

### 2. Device Management Flow

#### Test Case 2.1: View All Devices (User)
```
Steps:
1. Login as regular user
2. On dashboard, click "Devices" tab
3. Observe device list

Expected Results:
✓ List of devices loaded from backend
✓ Shows device name, type, status, condition
✓ Device count matches backend count
✓ No hardcoded/mock devices visible
```

#### Test Case 2.2: View My Devices
```
Steps:
1. Login as user
2. Click "My Devices" tab
3. Observe assigned devices

Expected Results:
✓ Only devices assigned to current user shown
✓ Shows assignment status
✓ Empty message if no devices assigned
```

---

### 3. Ticket/Issue Creation Flow

#### Test Case 3.1: Raise Repair Ticket
```
Steps:
1. Login as user
2. Click "Repair Ticket" tab
3. Select a device from dropdown
4. Choose priority: High/Medium/Low
5. Enter subject: "Screen is cracked"
6. Enter description: "The laptop screen has a crack on the bottom-right corner"
7. (Optional) Upload an image
8. Click "Raise Ticket"

Expected Results:
✓ Success message displayed
✓ Form clears after 2-3 seconds
✓ Ticket appears in "My Tickets" list immediately
✓ Ticket has auto-generated ticket_number (e.g., TKT-001)
✓ Status shows as "pending"
```

#### Test Case 3.2: Report Issue
```
Steps:
1. Login as user
2. Click "Report Issue" tab
3. Select device from dropdown
4. Choose issue type: Hardware/Software/Damage/Other
5. Enter description: "Application crashes on startup"
6. (Optional) Upload screenshot
7. Click "Submit Report"

Expected Results:
✓ Success message displayed
✓ Form clears
✓ Issue appears in "My Reports" history
✓ Issue type badge displayed
✓ Status progression visible in stepper
```

---

### 4. Admin Panel & Ticket Management Flow

#### Test Case 4.1: Admin Views Dashboard
```
Steps:
1. Login as admin (should auto-redirect to /admin/dashboard)
2. Observe Dashboard tab

Expected Results:
✓ Dashboard loads without errors
✓ Statistics card show real data from backend:
  - Total Devices
  - Assigned vs Available
  - Total Employees
  - Device type breakdown
```

#### Test Case 4.2: Admin Views Devices
```
Steps:
1. Navigate to Admin → Devices tab
2. Observe device list

Expected Results:
✓ All devices loaded from backend
✓ Shows device info, status, assigned employee
✓ No mock data visible
```

#### Test Case 4.3: Admin Views Employees
```
Steps:
1. Navigate to Admin → Employees tab
2. Observe employee list

Expected Results:
✓ All employees loaded from backend
✓ Shows employee info, department, device count
```

#### Test Case 4.4: Admin Manages Tickets
```
Steps:
1. Navigate to Admin → Ticket Requests tab
2. Observe list of pending tickets
3. Try to update a ticket status (if UI available)

Expected Results:
✓ Tickets from backend loaded
✓ Includes tickets from all users
✓ Can see ticket details
✓ Status updates work (if implemented)
```

---

### 5. Complete End-to-End Flow

```
Scenario: User reports issue → Admin sees it → Admin resolves it

Steps:
1. Login as User (testuser@example.com)
2. Go to "Report Issue" tab
3. Create new issue:
   - Device: Any device
   - Type: Hardware Problem
   - Description: "Device not turning on"
4. Submit and note the ticket number

5. Logout

6. Login as Admin (admin@example.com)
7. Go to Admin Panel (should auto-redirect)
8. Click "Ticket Requests" tab
9. Find the ticket created by testuser
10. Verify ticket details match what was submitted

11. Status should show as "pending" or similar
12. Admin can see user who submitted it

Expected Results:
✓ All steps complete without errors
✓ Data flows correctly from user to admin
✓ Information is consistent across both interfaces
✓ No data loss or duplication
```

---

### 6. Profile Management Flow

#### Test Case 6.1: User Profile View
```
Steps:
1. Login as user
2. (Click profile icon or navigate to /profile if available)

Expected Results:
✓ Shows current user's information from backend
✓ First name, last name, email displayed
✓ Department and role shown
✓ Join date displayed
✓ Profile picture (avatar) generated or stored
```

#### Test Case 6.2: Admin Profile View
```
Steps:
1. Login as admin
2. (Click profile icon or navigate to /admin/profile if available)

Expected Results:
✓ Shows admin information from backend
✓ Admin role displayed
✓ All profile fields populated
```

---

### 7. Image Upload Testing (Cloudinary Optional)

#### Test Case 7.1: Local Image Upload
```
Steps:
1. In "Report Issue" or "Raise Ticket"
2. Click "Upload Image"
3. Select a local image file (JPG/PNG)
4. Submit form

Expected Results:
✓ Image preview shown before submission
✓ Image can be removed
✓ Form submits with image data
✓ No errors in console
```

#### Test Case 7.2: Cloudinary Upload (if configured)
```
Steps:
1. Set VITE_CLOUDINARY_CLOUD_NAME and VITE_CLOUDINARY_UPLOAD_PRESET in .env.local
2. Reload frontend
3. In Issue/Ticket form, upload image
4. Submit form

Expected Results:
✓ Image uploaded to Cloudinary
✓ Cloudinary secure URL returned
✓ Image accessible in Cloudinary dashboard
✓ Form submission works with Cloudinary URL
```

---

## Error Testing

### Test Case E.1: Invalid Login
```
Steps:
1. Try to login with incorrect email or password
2. Verify error message displayed

Expected: ✓ Error message shown, not logged in
```

### Test Case E.2: Network Error
```
Steps:
1. Stop backend server
2. Try to load devices or create ticket
3. Verify error handling

Expected: ✓ Error page shown, user informed
```

### Test Case E.3: Unauthorized Access
```
Steps:
1. Login as regular user
2. Try to access /admin/dashboard directly
3. (If no auth guard, observe behavior)

Expected: ✓ Redirect to /devices or show unauthorized message
```

---

## Checklist for Production Readiness

- [ ] All user signup flow works (tested above)
- [ ] Login redirects users correctly (admin → /admin, user → /devices)
- [ ] All devices load from backend (no mock data)
- [ ] All employees/users visible to admin
- [ ] Tickets created by users
- [ ] Admin can see submitted tickets
- [ ] Profiles show real data
- [ ] Images can upload (or at least don't error)
- [ ] Error handling works gracefully
- [ ] No console errors
- [ ] Responsive design works on mobile views
- [ ] Environment variables configured for production

---

## Quick Test Commands

```bash
# Backend health check
curl http://localhost:8000/api/health

# List devices
curl http://localhost:8000/api/inventory/devices/

# List tickets
curl http://localhost:8000/api/inventory/tickets/

# Get current user
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8000/api/auth/user/
```

---

## Troubleshooting Test Failures

| Issue | Cause | Solution |
|-------|-------|----------|
| 404 on API calls | Backend not running | `python manage.py runserver` in backend dir |
| CORS errors | Frontend/backend URL mismatch | Check VITE_API_URL in .env.local |
| Login fails | Invalid credentials | Verify user exists in database |
| Redirect loop | Auth guard issues | Check AuthContext and routing |
| Mock data visible | Code not updated | Verify imports point to API services |
| Images won't upload | No Cloudinary setup | Either configure Cloudinary or use local storage |

---

## Production Testing

After deploying to Render (backend) and Vercel (frontend):

1. Test signup/login with production URLs
2. Verify data persists in production database
3. Check image uploads work with Cloudinary
4. Monitor error logs
5. Test on different browsers and devices
6. Load testing with multiple concurrent users
7. Security audit (check for exposed tokens, CORS issues)

---

## Sign-off

Date Tested: ___________
Tester: ___________
All tests passed: [ ] Yes [ ] No

Issues found: _________________________________
