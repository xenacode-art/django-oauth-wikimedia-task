# Toolforge Deployment Guide for django-oauth-erik

## Step 1: SSH to Toolforge
```bash
ssh xinacod@login.toolforge.org
```

## Step 2: Become the tool
```bash
become django-oauth-erik
```

## Step 3: Create directory structure
```bash
mkdir -p ~/www/python
cd ~/www/python
```

## Step 4: Create uwsgi.ini
```bash
cat > uwsgi.ini << 'UWSGIEOF'
[uwsgi]
check-static = /data/project/django-oauth-erik/www/python/static
UWSGIEOF
```

## Step 5: Clone the repository
```bash
git clone https://github.com/xenacode-art/django-oauth-wikimedia.git .
```

## Step 6: Create app.py for WSGI
```bash
cat > src/app.py << 'APPEOF'
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "oauth_app.settings")
app = get_wsgi_application()
APPEOF
```

## Step 7: Update settings.py for Toolforge
Add to settings.py:
```bash
nano src/oauth_app/settings.py
```
Add this line to ALLOWED_HOSTS:
```python
ALLOWED_HOSTS = [
    'django-oauth-erik.toolforge.org',
]
```

## Step 8: Setup virtual environment
```bash
webservice --backend=kubernetes python3.13 shell
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Step 9: Run migrations
```bash
python3 src/manage.py migrate
deactivate
exit
```

## Step 10: Set environment variables
```bash
toolforge envvars create MEDIAWIKI_CONSUMER_KEY
# Enter: 50c25d06ec49d43496b923948ab2be13

toolforge envvars create MEDIAWIKI_CONSUMER_SECRET
# Enter: 755897dd2bbec1a5a2821ebc55a1fc4af7d46309

toolforge envvars create MEDIAWIKI_CALLBACK
# Enter: https://django-oauth-erik.toolforge.org/oauth/complete/mediawiki/
```

## Step 11: Register PRODUCTION OAuth consumer
Go to: https://meta.wikimedia.org/wiki/Special:OAuthConsumerRegistration/propose/oauth1a

Settings:
- OAuth version: OAuth 1.0a
- Application name: "Django OAuth Erik (Production)"
- Callback URL: `https://django-oauth-erik.toolforge.org/`
- ✅ Check: "Allow consumer to specify a callback in requests"
- Grants: "User identity verification only"

Update the envvars with NEW production keys!

## Step 12: Start the webservice
```bash
webservice --backend=kubernetes python3.13 start
```

## Step 13: Check logs if issues
```bash
cat ~/uwsgi.log
```

## Step 14: Visit your app!
https://django-oauth-erik.toolforge.org

---

## Troubleshooting

### Check webservice status:
```bash
webservice --backend=kubernetes python3.13 status
```

### Restart webservice:
```bash
webservice --backend=kubernetes python3.13 restart
```

### View environment variables:
```bash
toolforge envvars list
```

### Update code from GitHub:
```bash
cd ~/www/python
git pull
webservice --backend=kubernetes python3.13 restart
```
