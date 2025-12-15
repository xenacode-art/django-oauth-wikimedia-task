# Django OAuth for Wikimedia

Production-ready boilerplate Django web app with OAuth authentication for Wikimedia wikis. Built during my Outreachy internship with Pywikibot.

**Live deployment:** https://django-oauth-erik.toolforge.org

**Features:**
- OAuth 1.0a authentication with Wikimedia
- REST API with Django REST Framework
- Vue.js 3 frontend with reactive components
- Multi-language support (English & Finnish)
- Pywikibot & mwclient integration for wiki operations
- Wiki database replica access via Django ORM
- Comprehensive unit tests with pytest
- Security checks (bandit, safety)
- Type checking with mypy
- Clean, environment-based configuration
- MariaDB database backend (Toolforge) with SQLite fallback (local)
- Automated deployment via GitHub Actions

## What it does

- Lets users log in with their Wikimedia account
- Passes OAuth credentials to Pywikibot for wiki operations
- Provides Django ORM models for querying MediaWiki database replicas
- Shows user profile with OAuth token information

## Requirements

- Python 3.11 or newer
- A Wikimedia OAuth consumer
## Getting started

Clone this repo and create a virtual environment:

```bash
git clone https://github.com/xenacode-art/django-oauth-wikimedia-task
cd my-first-django-oauth-app
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Register your OAuth consumer

Go to https://meta.wikimedia.org/wiki/Special:OAuthConsumerRegistration/propose/oauth1a

Fill out the form:
- Choose OAuth 1.0a
- Set callback to: `http://127.0.0.1:8080/oauth/complete/mediawiki/`
- Select "User identity verification only"
- **Important**: Check the box "Allow consumer to specify a callback in requests"

You'll get a consumer key and secret. Save these!

## Configuration

Set your OAuth credentials as environment variables:

```bash
export MEDIAWIKI_CONSUMER_KEY=your_key_here
export MEDIAWIKI_CONSUMER_SECRET=your_secret_here
export MEDIAWIKI_CALLBACK=http://127.0.0.1:8080/oauth/complete/mediawiki/
```

Or create a `.env` file (see `.env.example`)

## Running locally

```bash
cd src
python manage.py migrate
python manage.py runserver 127.0.0.1:8080
```

Open http://127.0.0.1:8080 and try logging in!

## How it's organized

```
src/
├── oauth_app/      - Django project settings and main URLs
├── user_profile/   - The app that handles login and profile display
│   ├── views.py    - Views: index, login, profile, search, statistics
│   ├── pywikibot_utils.py  - Pywikibot integration utilities
│   ├── mwclient_utils.py   - mwclient utilities (production-safe)
│   ├── urls.py     - URL patterns
│   └── templates/  - HTML templates with Vue.js components
├── api/            - REST API endpoints
│   ├── views.py    - API views for user data, wiki search, statistics
│   ├── serializers.py - Data serializers
│   └── urls.py     - API URL patterns
├── wiki_replica/   - Django ORM models for wiki database replicas
│   ├── models.py   - Models for MediaWiki tables (Page, Revision, User, etc.)
│   ├── router.py   - Database router for wiki replica
│   ├── utils.py    - Utility functions for querying wiki data
│   └── admin.py    - Read-only admin interface
└── manage.py
```

## Key Features

### 1. REST API
Full REST API for all application features:

```bash
# User endpoints (require authentication)
GET /api/user/profile/              # Get user profile data
GET /api/user/contributions/        # Get recent contributions

# Wiki endpoints (public)
GET /api/wiki/search/?q=test        # Search wiki pages
GET /api/wiki/statistics/           # Get wiki statistics
```

### 2. Vue.js Frontend
Reactive Vue 3 components for:
- User profile with dynamic data loading
- Real-time wiki search with debouncing
- Interactive statistics dashboard
- All pages use clean, modern UI design

### 3. Multi-Language Support
Built-in internationalization with language switcher:
- English (default)
- Finnish (Suomi)
- Easy to add more languages

Switch languages from any page using the dropdown in the header.

### 4. Pywikibot & mwclient Integration
Use Django OAuth credentials to perform wiki operations:

```python
from user_profile.mwclient_utils import get_user_info, make_edit_as_user

# Get user information
user_info = get_user_info(request.user)

# Make an edit as the user
make_edit_as_user(request.user, 'User:Example/Sandbox', 'Content', 'Summary')
```

### 5. Wiki Replica Access
Query MediaWiki database replicas using Django ORM:

```python
from wiki_replica.utils import get_recent_changes, search_pages

# Get recent changes
changes = get_recent_changes(limit=10)

# Search for pages
results = search_pages('Python', limit=20)
```

### 6. Testing & Quality Assurance
Comprehensive testing and security:

```bash
# Run all tests
pytest

# Security checks
bandit -r src/ -c .bandit
safety check

# Type checking
mypy src/

# Or run everything at once
make all          # Linux/Mac
run-checks.bat    # Windows
```

## Detailed Documentation

See `IMPLEMENTATION_GUIDE.md` for:
- Complete API reference
- Usage examples
- Configuration guide
- Local development setup
- Troubleshooting tips

## Tech Stack

**Backend:**
- Django 6.0
- Django REST Framework 3.15.2
- social-auth-app-django 5.6.0
- PyMySQL 1.1.1

**Wiki Integration:**
- Pywikibot 9.5.0
- mwclient 0.11.0

**Frontend:**
- Vue.js 3 (CDN)
- Modern CSS with responsive design

**Testing & Quality:**
- pytest 8.3.4
- pytest-django 4.9.0
- bandit 1.8.0
- safety 3.2.11
- mypy 1.13.0

---

Built by Erik (Xinacod) as part of Outreachy 2025
