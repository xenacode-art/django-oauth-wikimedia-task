#!/bin/bash
# Toolforge Deployment Script for django-oauth-erik

echo "=== Deploying Django OAuth App to Toolforge ==="

# Step 1: Become the tool
echo "Step 1: Switching to tool account..."
become django-oauth-erik

# Step 2: Create directory structure
echo "Step 2: Creating directory structure..."
mkdir -p ~/www/python
cd ~/www/python

# Step 3: Clone the repository
echo "Step 3: Cloning repository..."
git clone https://github.com/xenacode-art/django-oauth-wikimedia.git .

# Step 4: Create uwsgi.ini
echo "Step 4: Creating uwsgi.ini..."
cat > uwsgi.ini << 'UWSGI'
[uwsgi]
check-static = /data/project/django-oauth-erik/www/python/static
UWSGI

# Step 5: Create app.py
echo "Step 5: Creating app.py..."
cat > src/app.py << 'APPPY'
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "oauth_app.settings")
app = get_wsgi_application()
APPPY

# Step 6: Set up virtual environment
echo "Step 6: Setting up virtual environment..."
webservice --backend=kubernetes python3.13 shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Step 7: Run migrations
echo "Step 7: Running migrations..."
python3 src/manage.py migrate

deactivate

echo "=== Deployment complete! ==="
echo "Next steps:"
echo "1. Set environment variables with: toolforge envvars create"
echo "2. Register production OAuth consumer"
echo "3. Start webservice with: webservice --backend=kubernetes python3.13 start"
