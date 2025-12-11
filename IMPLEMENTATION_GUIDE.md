# Implementation Guide: Django OAuth with Pywikibot and Wiki Replica

This guide documents the implementation of three major features:
1. Passing OAuth credentials from Django to Pywikibot
2. Improved database configuration using environment variables
3. Wiki database replica access with Django ORM models

## 1. Pywikibot Integration

### Overview
The application now integrates Django OAuth credentials with Pywikibot, allowing you to perform wiki operations on behalf of authenticated users.

### Files Added
- `src/user_profile/pywikibot_utils.py` - Utility functions for Pywikibot integration

### Key Functions

#### `get_pywikibot_site_for_user(user, wiki='meta', family='wikimedia')`
Creates an authenticated Pywikibot Site instance using the user's OAuth credentials.

```python
from user_profile.pywikibot_utils import get_pywikibot_site_for_user

# In a view with an authenticated user
site = get_pywikibot_site_for_user(request.user)
# Now you can use the site object to interact with the wiki
```

#### `get_user_edit_count(user, wiki='meta', family='wikimedia')`
Retrieves the edit count for a user.

```python
from user_profile.pywikibot_utils import get_user_edit_count

edit_count = get_user_edit_count(request.user)
```

#### `get_user_contributions(user, total=10, wiki='meta', family='wikimedia')`
Gets recent contributions for a user.

```python
from user_profile.pywikibot_utils import get_user_contributions

contributions = get_user_contributions(request.user, total=5)
for contrib in contributions:
    print(f"{contrib['page']}: {contrib['comment']}")
```

#### `make_edit_as_user(user, page_title, new_text, summary, wiki='meta', family='wikimedia')`
Makes an edit to a wiki page using the user's OAuth credentials.

```python
from user_profile.pywikibot_utils import make_edit_as_user

success = make_edit_as_user(
    request.user,
    'User:YourUsername/Sandbox',
    'New page content',
    'Testing edit via OAuth'
)
```

### Usage in Views
The profile view has been updated to demonstrate OAuth credential access:

```python
@login_required()
def profile(request):
    context = {}
    try:
        social_auth = UserSocialAuth.objects.get(user=request.user, provider='mediawiki')
        extra_data = social_auth.extra_data
        access_token = extra_data.get('access_token', {})

        context['oauth_token'] = access_token.get('oauth_token', 'N/A')
        context['has_oauth'] = True

        # Uncomment to use Pywikibot features
        # context['edit_count'] = get_user_edit_count(request.user)
        # context['contributions'] = get_user_contributions(request.user, total=5)
    except UserSocialAuth.DoesNotExist:
        context['has_oauth'] = False

    return render(request, 'user_profile/profile.dtl', context)
```

## 2. Improved Database Configuration

### Overview
Database configuration has been simplified to use `read_default_file` for MariaDB credentials and environment variables for configuration.

### Changes to `settings.py`

#### Before:
```python
import configparser
config = configparser.ConfigParser()
config.read(os.path.expanduser('~/replica.my.cnf'))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 's57230__django_oauth_erik_p',
        'USER': config['client']['user'],
        'PASSWORD': config['client']['password'],
        # ...
    }
}
```

#### After:
```python
db_name = os.environ.get('TOOLSDB_NAME', 's57230__django_oauth_erik')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': db_name,  # Private database (no _p suffix)
        'HOST': 'tools.db.svc.wikimedia.cloud',
        'PORT': '3306',
        'OPTIONS': {
            'read_default_file': os.path.expanduser('~/replica.my.cnf'),
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        },
    }
}
```

### Benefits
1. **Simpler code**: No need to manually parse the config file
2. **More secure**: Credentials are read directly by the MySQL driver
3. **Configurable**: Database name can be set via environment variable
4. **Private by default**: Database name doesn't have `_p` suffix (making it private)

### Environment Variables

Set these in Toolforge using `toolforge envvars`:

```bash
# On Toolforge
toolforge envvars set TOOLSDB_NAME s57230__django_oauth_erik
toolforge envvars set WIKI_REPLICA metawiki
toolforge envvars set TOOLFORGE_DEPLOYMENT true
```

For local development, create a `.env` file (see `.env.example`).

## 3. Wiki Replica Database Access

### Overview
The application now includes Django ORM models for accessing MediaWiki database replicas on Toolforge.

### Files Added
- `src/wiki_replica/` - New Django app for wiki replica models
  - `models.py` - Django models mapped to MediaWiki tables
  - `router.py` - Database router for wiki replica queries
  - `utils.py` - Utility functions for common queries
  - `admin.py` - Read-only admin interface

### Database Configuration

The application now supports two databases:

```python
DATABASES = {
    'default': {
        # Your tool's database for Django models
        'NAME': 's57230__django_oauth_erik',
        'HOST': 'tools.db.svc.wikimedia.cloud',
    },
    'wiki_replica': {
        # Wiki replica database (read-only)
        'NAME': 'metawiki_p',
        'HOST': 'metawiki.analytics.db.svc.wikimedia.cloud',
    }
}

DATABASE_ROUTERS = ['wiki_replica.router.WikiReplicaRouter']
```

The database router automatically directs queries for `wiki_replica` models to the wiki replica database.

### Available Models

All models are in `wiki_replica.models`:

- **Page**: Wiki pages metadata
- **Revision**: Page revisions
- **Actor**: User/IP actors
- **User**: Registered users
- **RecentChanges**: Recent changes (rolling window)
- **Logging**: Log entries

### Usage Examples

#### Get Recent Changes
```python
from wiki_replica.utils import get_recent_changes

recent_changes = get_recent_changes(limit=20)
for change in recent_changes:
    print(f"{change.rc_title} by {change.rc_actor} at {change.rc_timestamp}")
```

#### Find a Page
```python
from wiki_replica.utils import get_page_by_title

page = get_page_by_title('Main Page', namespace=0)
if page:
    print(f"Page ID: {page.page_id}, Length: {page.page_len}")
```

#### Get User Information
```python
from wiki_replica.utils import get_user_by_name, get_user_edit_count_from_db

user = get_user_by_name('ExampleUser')
if user:
    print(f"Edit count: {user.user_editcount}")
    print(f"Registration: {user.user_registration}")

# Or use the utility function
edit_count = get_user_edit_count_from_db('ExampleUser')
```

#### Search Pages
```python
from wiki_replica.utils import search_pages

results = search_pages('Python', namespace=0, limit=10)
for page in results:
    print(f"{page.page_title} ({page.page_len} bytes)")
```

#### Get Statistics
```python
from wiki_replica.utils import get_page_statistics

stats = get_page_statistics()
print(f"Total pages: {stats['total_pages']}")
print(f"Content pages: {stats['content_pages']}")
print(f"Redirects: {stats['redirects']}")
```

### Using Models Directly

You can also use Django ORM directly:

```python
from wiki_replica.models import Page, Revision, RecentChanges

# Get all pages in main namespace
pages = Page.objects.filter(page_namespace=0)[:100]

# Get revisions for a page
revisions = Revision.objects.filter(rev_page=12345).order_by('-rev_timestamp')[:10]

# Get recent bot edits
bot_edits = RecentChanges.objects.filter(rc_bot=True).order_by('-rc_timestamp')[:20]
```

### Local Development with SSH Tunnel

To test wiki replica access locally, you need to set up an SSH tunnel:

```bash
# Terminal 1: SSH tunnel for tools database
ssh -L 3306:tools.db.svc.wikimedia.cloud:3306 USERNAME@login.toolforge.org

# Terminal 2: SSH tunnel for wiki replica
ssh -L 3307:metawiki.analytics.db.svc.wikimedia.cloud:3306 USERNAME@login.toolforge.org

# Then update your local settings to use localhost:3306 and localhost:3307
```

## Configuration Reference

### Environment Variables

Create a `.env` file or set these in Toolforge:

```bash
# Django
SECRET_KEY=your-secret-key-here

# OAuth
MEDIAWIKI_CONSUMER_KEY=your_oauth_consumer_key
MEDIAWIKI_CONSUMER_SECRET=your_oauth_consumer_secret
MEDIAWIKI_CALLBACK=https://yourtool.toolforge.org/oauth/complete/mediawiki/

# Deployment
TOOLFORGE_DEPLOYMENT=true

# Database
TOOLSDB_NAME=s57230__django_oauth_erik
WIKI_REPLICA=metawiki
```

### Supported Wiki Codes

For `WIKI_REPLICA`, you can use any valid wiki code:
- `metawiki` - Meta-Wiki
- `enwiki` - English Wikipedia
- `commonswiki` - Wikimedia Commons
- `wikidatawiki` - Wikidata
- etc.

## Testing

### Local Testing (without Toolforge)

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run migrations:
```bash
cd src
python manage.py migrate
```

3. Run the development server:
```bash
python manage.py runserver 127.0.0.1:8080
```

Note: Pywikibot and wiki replica features require Toolforge or SSH tunnels to work.

### Toolforge Testing

1. Deploy to Toolforge:
```bash
./deploy-to-toolforge.sh
```

2. Set environment variables:
```bash
toolforge envvars set TOOLSDB_NAME s57230__django_oauth_erik
toolforge envvars set WIKI_REPLICA metawiki
toolforge envvars set TOOLFORGE_DEPLOYMENT true
```

3. Restart the webservice:
```bash
toolforge webservice restart
```

## Troubleshooting

### OAuth Token Issues
If Pywikibot functions fail, check:
- User is authenticated via OAuth
- OAuth credentials are stored in social_django UserSocialAuth
- Access token contains both `oauth_token` and `oauth_token_secret`

### Wiki Replica Connection Issues
If wiki replica queries fail:
- Verify `WIKI_REPLICA` environment variable is set correctly
- Check that the replica database host is accessible
- Ensure `~/replica.my.cnf` exists and has correct permissions
- Verify the wiki code matches an actual wiki (e.g., `metawiki`, not `meta`)

### Database Router Issues
If queries go to the wrong database:
- Ensure `DATABASE_ROUTERS` includes `'wiki_replica.router.WikiReplicaRouter'`
- Check that wiki_replica models have `app_label = 'wiki_replica'` in Meta
- Verify `managed = False` is set for all wiki_replica models

## Next Steps

1. **Automated Deployment**: Set up GitHub Actions for automatic deployment
2. **Error Handling**: Add better error handling for Pywikibot operations
3. **Caching**: Implement caching for wiki replica queries
4. **API Endpoints**: Create REST API endpoints for wiki data
5. **User Interface**: Build UI for viewing wiki statistics and recent changes
