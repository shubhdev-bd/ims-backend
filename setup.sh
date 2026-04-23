#!/bin/bash

# IMS System Setup Script
# This script automates the setup of the IMS system

set -e

echo "=========================================="
echo "IMS System Setup"
echo "=========================================="
echo ""

# Check if we're in the correct directory
if [ ! -f "manage.py" ]; then
    echo "❌ Error: manage.py not found. Please run this script from the Django backend directory."
    exit 1
fi

echo "📦 Running migrations..."
python3 manage.py migrate
echo "✅ Migrations complete"
echo ""

echo "👥 Creating test users..."
python3 manage.py create_users
echo "✅ Test users created"
echo ""

echo "📱 Loading inventory from JSON..."
python3 manage.py load_inventory --file ../inventry.json
echo "✅ Inventory loaded"
echo ""

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Google Apps Script Setup:"
echo "   - See APPSCRIPT_SETUP.md for detailed instructions"
echo "   - Copy the script code from Documentation/"
echo "   - Deploy as a web app"
echo "   - Update Django .env with APPS_SCRIPT_URL"
echo ""
echo "2. Create an admin user (optional):"
echo "   - python3 manage.py createsuperuser"
echo ""
echo "3. Start the development server:"
echo "   - python3 manage.py runserver"
echo ""
echo "4. Test users created:"
echo "   - arun@believersdestination.com"
echo "   - vikas@believersdestination.com"
echo "   - vamika@believersdestination.com"
echo "   - shubh@believersdestination.com"
echo "   - nikita@believersdestination.com"
echo "   (All with password: password123)"
echo ""
echo "5. Frontend setup:"
echo "   - Navigate to frontend directory"
echo "   - npm install && npm run dev"
echo ""
echo "=========================================="
echo ""
