# Deployment Checklist

This checklist helps you deploy the updated Django OAuth app with Pywikibot and wiki replica features to Toolforge.

## Pre-Deployment Steps

### 1. Update Dependencies on Toolforge

SSH into Toolforge and update the requirements:

```bash
ssh USERNAME@login.toolforge.org
become django-oauth-erik  # or your tool name
cd ~/www/python
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Set Environment Variables

Configure the environment variables using `toolforge envvars`:

```bash
# Database configuration
toolforge envvars set TOOLSDB_NAME s57230__django_oauth_erik
toolforge envvars set WIKI_REPLICA metawiki

# Mark as Toolforge deployment
toolforge envvars set TOOLFORGE_DEPLOYMENT true

# OAuth credentials (if not already set)
toolforge envvars set MEDIAWIKI_CONSUMER_KEY your_consumer_key
toolforge envvars set MEDIAWIKI_CONSUMER_SECRET your_consumer_secret
toolforge envvars set MEDIAWIKI_CALLBACK https://django-oauth-erik.toolforge.org/oauth/complete/mediawiki/

# Verify environment variables
toolforge envvars list
```

### 3. Create Private Database

Ensure your database name doesn't have the `_p` suffix for privacy:

```bash
# Check current database
sql s57230__django_oauth_erik

# If it has _p suffix, you may need to create a new one
# The database should be automatically created when you run migrations
```

### 4. Run Migrations

```bash
cd ~/www/python/src
python manage.py migrate --database=default
```

Note: Don't migrate wiki_replica - those tables already exist in the wiki replica database.

### 5. Collect Static Files (if applicable)

```bash
python manage.py collectstatic --noinput
```

## Deployment

### Option 1: Manual Deployment

```bash
# On your local machine
git add .
git commit -m "Add Pywikibot integration and wiki replica access"
git push origin master

# On Toolforge
ssh USERNAME@login.toolforge.org
become django-oauth-erik
cd ~/www/python
git pull origin master
toolforge webservice restart
```

### Option 2: Automated Deployment via GitHub Actions

If you have GitHub Actions set up, just push your changes:

```bash
git add .
git commit -m "Add Pywikibot integration and wiki replica access"
git push origin master
```

The workflow will automatically deploy to Toolforge.

## Post-Deployment Verification

### 1. Check Webservice Status

```bash
toolforge webservice status
```

Expected output:
```
django-oauth-erik: Your webservice is running
```

### 2. Check Logs

```bash
tail -f ~/www/python/uwsgi.log
```

Look for any errors during startup.

### 3. Test OAuth Flow

1. Visit https://django-oauth-erik.toolforge.org
2. Click "Log in"
3. Complete OAuth authentication
4. Verify you can see your profile with OAuth token information

### 4. Test Pywikibot Integration (Optional)

Update `src/user_profile/views.py` to uncomment the Pywikibot code:

```python
# Uncomment these lines
try:
    context['edit_count'] = get_user_edit_count(request.user)
    context['contributions'] = get_user_contributions(request.user, total=5)
except Exception as e:
    context['pywikibot_error'] = str(e)
```

Then restart and test.

### 5. Test Wiki Replica Access (Optional)

Create a test view to verify wiki replica access:

```python
from wiki_replica.utils import get_recent_changes, get_page_statistics

def wiki_stats(request):
    stats = get_page_statistics()
    recent = get_recent_changes(limit=10)
    return render(request, 'wiki_stats.dtl', {
        'stats': stats,
        'recent': recent
    })
```

## Troubleshooting

### Issue: ModuleNotFoundError

If you get import errors:

```bash
# Reinstall dependencies
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Issue: Database Connection Failed

Check your database configuration:

```bash
# Verify replica.my.cnf exists
cat ~/replica.my.cnf

# Should contain:
# [client]
# user=s57230
# password=...

# Test database connection
sql s57230__django_oauth_erik
```

### Issue: Wiki Replica Connection Failed

Verify wiki replica settings:

```bash
# Check environment variable
toolforge envvars list | grep WIKI_REPLICA

# Test connection to wiki replica
sql metawiki_p

# If that fails, check the host
ping metawiki.analytics.db.svc.wikimedia.cloud
```

### Issue: OAuth Not Working

1. Verify OAuth consumer is still active:
   - Visit https://meta.wikimedia.org/wiki/Special:OAuthListConsumers
   - Find your consumer and check status

2. Check environment variables:
   ```bash
   toolforge envvars list | grep MEDIAWIKI
   ```

3. Verify callback URL matches:
   - Should be: `https://yourtool.toolforge.org/oauth/complete/mediawiki/`

## Performance Optimization

### 1. Database Connection Pooling

Consider adding connection pooling for better performance:

```python
# In settings.py
DATABASES['default']['OPTIONS']['connect_timeout'] = 5
```

### 2. Caching Wiki Replica Queries

Add caching to frequently accessed wiki data:

```python
from django.core.cache import cache

def get_cached_recent_changes(limit=10):
    cache_key = f'recent_changes_{limit}'
    data = cache.get(cache_key)
    if data is None:
        data = list(get_recent_changes(limit))
        cache.set(cache_key, data, 300)  # Cache for 5 minutes
    return data
```

### 3. Limit Query Results

Always use `limit` or `[:N]` when querying wiki replicas:

```python
# Good
pages = Page.objects.filter(page_namespace=0)[:100]

# Bad (could return millions of rows)
pages = Page.objects.filter(page_namespace=0)
```

## Rollback Plan

If something goes wrong:

```bash
# SSH to Toolforge
ssh USERNAME@login.toolforge.org
become django-oauth-erik

# Revert to previous version
cd ~/www/python
git log --oneline  # Find the commit hash to revert to
git checkout <previous-commit-hash>

# Restart webservice
toolforge webservice restart
```

## Security Checklist

- [ ] Database name doesn't have `_p` suffix (private database)
- [ ] `SECRET_KEY` is set via environment variable (not hardcoded)
- [ ] `DEBUG = False` in production (or controlled via env var)
- [ ] OAuth credentials are in environment variables
- [ ] `~/replica.my.cnf` has correct permissions (0600)
- [ ] No credentials in Git repository
- [ ] ALLOWED_HOSTS includes your tool domain

## Next Steps After Deployment

1. Monitor logs for errors:
   ```bash
   tail -f ~/www/python/uwsgi.log
   ```

2. Test all features:
   - OAuth login
   - Profile page
   - Pywikibot integration (if enabled)
   - Wiki replica queries (if enabled)

3. Update documentation:
   - Add any deployment-specific notes
   - Document any issues encountered

4. Create backup:
   ```bash
   mysqldump s57230__django_oauth_erik > backup.sql
   ```

5. Set up monitoring:
   - Check https://yourtool.toolforge.org/admin periodically
   - Monitor database usage
   - Watch for errors in logs

## Support

If you encounter issues:

1. Check Toolforge documentation: https://wikitech.wikimedia.org/wiki/Help:Toolforge
2. Ask in #wikimedia-cloud on IRC
3. Create a Phabricator task: https://phabricator.wikimedia.org

---

Good luck with your deployment!
