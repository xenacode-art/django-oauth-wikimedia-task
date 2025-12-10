# Django OAuth for Wikimedia

Django web app with OAuth authentication for Wikimedia wikis. Built during my Outreachy internship with Pywikibot.

**Live deployment:** https://django-oauth-erik.toolforge.org

**Features:**
- Clean git history
- Automated deployment via GitHub Actions
- MariaDB database backend
- OAuth 1.0a authentication

## What it does

- Lets users log in with their Wikimedia account
- Shows their username after logging in
- Uses OAuth 1.0a (the standard for Wikimedia)

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
│   ├── views.py    - Three simple views: index, login, profile
│   ├── urls.py     - URL patterns
│   └── templates/  - HTML templates
└── manage.py
```

## What I learned

This was my first time setting up OAuth with Wikimedia. The trickiest part was figuring out that you need to check the "Allow consumer to specify callback" box when registering the OAuth consumer - without it you get cryptic errors about "oob" callbacks.

## Next steps

- Deploy this to Toolforge
- Set up automated deployment with GitHub Actions

## Stack

- Django 6.0
- social-auth-app-django 5.6.0

---

Built by Erik (Xinacod) as part of Outreachy 2025
