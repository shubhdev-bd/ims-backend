# Image Storage Setup Guide

## Overview
This IMS application supports image uploads for device profiles and issue/ticket attachments. You have two options for storing images:

### Option 1: Cloudinary (Recommended - FREE)
Cloudinary provides a generous free tier with 25 GB of storage monthly.

### Option 2: Local Storage (Development)
For development/testing, images can be stored locally in the `/media` folder.

---

## Option 1: Setup Cloudinary (Recommended)

### Step 1: Create a Free Cloudinary Account

1. Go to [https://cloudinary.com/users/register/free](https://cloudinary.com/users/register/free)
2. Sign up with your email
3. Verify your email
4. You'll be redirected to your Cloudinary Dashboard

### Step 2: Get Your API Credentials

1. Log into [https://cloudinary.com/console](https://cloudinary.com/console)
2. Copy your **Cloud Name** (visible in the API Environment variables section)
3. Click on the "Account" or "Settings" gear icon
4. Find **API Key** and **API Secret**
5. Note: Keep API Secret private - never commit to version control

### Step 3: Configure Environment Variables

#### Backend (.env file)

```env
# Cloudinary configuration
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret

# OR use Cloudinary URL format (preferred)
CLOUDINARY_URL=cloudinary://api_key:api_secret@cloud_name
```

#### Frontend (.env.local or .env.production)

```env
VITE_CLOUDINARY_CLOUD_NAME=your_cloud_name
VITE_CLOUDINARY_UPLOAD_PRESET=your_upload_preset
```

### Step 4: Create an Upload Preset (Frontend uploads)

1. Log into Cloudinary Console
2. Go to Settings → Upload → Add Upload Preset
3. Choose "Unsigned" mode (allows frontend uploads without backend)
4. Set Folder to: `ims-system/uploads`
5. Save and copy the **Upload Preset** name

### Step 5: Create API Secret Key (Backend uploads)

Already obtained in Step 2. Store safely in your `.env` file.

### Installation

#### Django Backend
```bash
pip install cloudinary
```

#### React Frontend
```bash
npm install cloudinary-react next-cloudinary
```

---

## Option 2: Local Storage (Development Only)

### Configuration

The backend is already configured for local media storage:
- Media files stored in: `/media/` directory
- Served via: `http://localhost:8000/media/`

### Setup

```bash
# Create media directory
mkdir -p media

# Ensure permissions
chmod 755 media
```

### Usage

In development, uploaded files are stored locally and served directly.

**Note:** Local storage is only suitable for development. For production, use Cloudinary.

---

## Image Upload Implementation

### Frontend Image Upload Flow

```javascript
// Using Cloudinary Upload Widget (Recommended)
import { CldUploadWidget } from 'next-cloudinary';

<CldUploadWidget
  uploadPreset={import.meta.env.VITE_CLOUDINARY_UPLOAD_PRESET}
  onSuccess={(result) => {
    const imageUrl = result.info.secure_url;
    // Send to backend
  }}
/>
```

### Backend Image Handling

Images from Cloudinary are stored as URLs. Save the URL path to the database:

```python
# models.py
class Device(models.Model):
    # ...
    image_url = models.URLField(blank=True, null=True)  # Cloudinary URL
```

### Form Submission with Images

```javascript
// When submitting form with image
const formData = new FormData();
formData.append('device_name', deviceName);
formData.append('image_url', imageUrl); // Cloudinary URL

await axios.post('/api/devices/', formData);
```

---

## Production Deployment

### Render.com Backend

1. Add Cloudinary variables to Render Environment:
   ```
   CLOUDINARY_CLOUD_NAME=your_cloud_name
   CLOUDINARY_API_KEY=your_api_key
   CLOUDINARY_API_SECRET=your_api_secret
   ```

2. For security, store these in Render's Secret Files or Environment

### Vercel Frontend

1. Add to Vercel Project Settings → Environment Variables:
   ```
   VITE_CLOUDINARY_CLOUD_NAME=your_cloud_name
   VITE_CLOUDINARY_UPLOAD_PRESET=your_upload_preset
   ```

2. Redeploy frontend after adding variables

---

## File Size Limits

### Cloudinary Free Plan
- Max file: 100 MB
- Monthly quota: 25 GB (generous)
- Auto-optimized delivery

### Local Storage
- Limited by disk space
- No automatic optimization

---

## Troubleshooting

### Issue: Images not uploading
- Check Cloudinary credentials in .env
- Verify Upload Preset is set to "Unsigned"
- Check CORS settings if frontend and backend on different domains

### Issue: Images not appearing in frontend
- Verify Cloudinary URL is accessible
- Check image permissions in Cloudinary Console
- Ensure HTTPS is used for all image URLs

### Issue: API Secret exposed
- **Immediately** regenerate API Key in Cloudinary Console
- Update .env files
- Redeploy application

---

## Free Alternatives

If Cloudinary doesn't work for you:

1. **imgbb.com** - Free API, simple usage
2. **Imgur** - Free hosting, but limits on uploads
3. **Filestack.com** - Free tier available
4. **Local + AWS S3** - (Not free, but option for later)

For this project, **Cloudinary is recommended** as it's the easiest to set up and most scalable for your needs.

---

## Next Steps

1. Create Cloudinary account
2. Configure .env files with credentials
3. Test file upload in development
4. Deploy to production with environment variables set
5. Monitor Cloudinary dashboard for storage usage

For questions, refer to [Cloudinary Documentation](https://cloudinary.com/documentation)
