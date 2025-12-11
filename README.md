# Django OAuth for Wikimedia

Django web app with OAuth authentication for Wikimedia wikis. Built during my Outreachy internship with Pywikibot.

**Live deployment:** https://django-oauth-erik.toolforge.org

**Features:**
- OAuth 1.0a authentication with Wikimedia
- Pywikibot integration - use OAuth credentials to make wiki edits
- Wiki database replica access via Django ORM
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
│   ├── views.py    - Views: index, login, profile
│   ├── pywikibot_utils.py  - Pywikibot integration utilities
│   ├── urls.py     - URL patterns
│   └── templates/  - HTML templates
├── wiki_replica/   - Django ORM models for wiki database replicas
│   ├── models.py   - Models for MediaWiki tables (Page, Revision, User, etc.)
│   ├── router.py   - Database router for wiki replica
│   ├── utils.py    - Utility functions for querying wiki data
│   └── admin.py    - Read-only admin interface
└── manage.py
```

## New Features

### 1. Pywikibot Integration
Use Django OAuth credentials to perform wiki operations via Pywikibot:

```python
from user_profile.pywikibot_utils import get_user_edit_count, make_edit_as_user

# Get user's edit count
edit_count = get_user_edit_count(request.user)

# Make an edit as the user
make_edit_as_user(request.user, 'User:Example/Sandbox', 'Content', 'Summary')
```

See `IMPLEMENTATION_GUIDE.md` for full documentation.

### 2. Wiki Replica Access
Query MediaWiki database replicas using Django ORM:

```python
from wiki_replica.utils import get_recent_changes, search_pages, get_page_by_title

# Get recent changes
changes = get_recent_changes(limit=10)

# Search for pages
results = search_pages('Python', limit=20)

# Get page by title
page = get_page_by_title('Main Page')
```

### 3. Improved Configuration
- Uses environment variables for all configuration
- Cleaner database setup with `read_default_file`
- Private database by default (no `_p` suffix)

## Detailed Documentation

See `IMPLEMENTATION_GUIDE.md` for:
- Complete API reference
- Usage examples
- Configuration guide
- Local development setup
- Troubleshooting tips

## Stack

- Django 6.0
- social-auth-app-django 5.6.0
- Pywikibot 9.5.0
- PyMySQL 1.1.1

---

Built by Erik (Xinacod) as part of Outreachy 2025
