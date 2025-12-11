"""
Utility functions for integrating mwclient with Django OAuth credentials.

This module provides OAuth-safe functions for multi-user web applications.
Unlike Pywikibot (which caches credentials globally), mwclient creates
isolated client instances per request, making it safe for concurrent users.

WHY MWCLIENT INSTEAD OF PYWIKIBOT FOR WEB APPS:
- Thread-safe: No global state or credential caching
- Concurrent users: Each user gets their own isolated client
- OAuth-friendly: Designed for OAuth 1.0a authentication
- Web-optimized: Better for request/response cycles

Use this module for user-authenticated API operations in Django views.
"""

import mwclient
from social_django.models import UserSocialAuth


def get_mwclient_for_user(user, wiki_url='https://meta.wikimedia.org'):
    """
    Get an OAuth-authenticated mwclient Site instance for a user.

    This function creates a NEW client instance for each call, avoiding
    the credential caching issues that Pywikibot has in multi-user environments.

    Args:
        user: Django User object with social auth credentials
        wiki_url: Full URL to the wiki (default: 'https://meta.wikimedia.org')

    Returns:
        mwclient.Site: Authenticated mwclient site instance

    Raises:
        UserSocialAuth.DoesNotExist: If user has no social auth credentials
        ValueError: If OAuth credentials are incomplete

    Example:
        >>> site = get_mwclient_for_user(request.user)
        >>> page = site.pages['User:Example/Sandbox']
        >>> print(page.text())
    """
    try:
        social_auth = UserSocialAuth.objects.get(user=user, provider='mediawiki')
    except UserSocialAuth.DoesNotExist:
        raise UserSocialAuth.DoesNotExist(
            f"No MediaWiki OAuth credentials found for user {user.username}"
        )

    extra_data = social_auth.extra_data
    access_token = extra_data.get('access_token', {})

    oauth_token = access_token.get('oauth_token')
    oauth_token_secret = access_token.get('oauth_token_secret')

    if not oauth_token or not oauth_token_secret:
        raise ValueError(
            "OAuth access token or secret is missing from social auth data"
        )

    # Extract host and path from wiki_url
    # Example: 'https://meta.wikimedia.org' -> host='meta.wikimedia.org', path='/w/'
    from urllib.parse import urlparse
    parsed = urlparse(wiki_url)
    host = parsed.netloc
    # Wikimedia sites use /w/ as the path to api.php
    path = '/w/'
    scheme = parsed.scheme

    # Get OAuth consumer credentials from Django settings
    from django.conf import settings
    consumer_token = settings.SOCIAL_AUTH_MEDIAWIKI_KEY
    consumer_secret = settings.SOCIAL_AUTH_MEDIAWIKI_SECRET

    # Create mwclient Site instance with OAuth 1.0a
    site = mwclient.Site(
        host=host,
        path=path,
        scheme=scheme,
        consumer_token=consumer_token,
        consumer_secret=consumer_secret,
        access_token=oauth_token,
        access_secret=oauth_token_secret
    )

    return site


def get_user_info(user, wiki_url='https://meta.wikimedia.org'):
    """
    Get user information including edit count using public API (no OAuth needed).

    This function uses the public MediaWiki API to fetch user data.
    OAuth is not needed since this information is publicly available.

    Args:
        user: Django User object with social auth credentials
        wiki_url: Full URL to the wiki (default: 'https://meta.wikimedia.org')

    Returns:
        dict: User information including:
            - name: Username
            - editcount: Number of edits
            - registration: Registration timestamp
            - groups: List of user groups

    Example:
        >>> info = get_user_info(request.user)
        >>> print(f"Edit count: {info['editcount']}")
    """
    # Get the Wikimedia username from social auth
    from social_django.models import UserSocialAuth
    try:
        social_auth = UserSocialAuth.objects.get(user=user, provider='mediawiki')
        username = social_auth.extra_data.get('username', user.username)
    except UserSocialAuth.DoesNotExist:
        username = user.username

    # Use public API (no OAuth) to get user info
    from urllib.parse import urlparse
    import requests

    parsed = urlparse(wiki_url)
    api_url = f"{parsed.scheme}://{parsed.netloc}/w/api.php"

    params = {
        'action': 'query',
        'list': 'users',
        'ususers': username,
        'usprop': 'editcount|registration|groups',
        'format': 'json'
    }

    response = requests.get(api_url, params=params)
    data = response.json()

    if 'query' in data and 'users' in data['query'] and len(data['query']['users']) > 0:
        user_data = data['query']['users'][0]
        return {
            'name': user_data.get('name', username),
            'editcount': user_data.get('editcount', 0),
            'registration': user_data.get('registration'),
            'groups': user_data.get('groups', [])
        }

    # Fallback if API call fails
    return {
        'name': username,
        'editcount': 0,
        'registration': None,
        'groups': []
    }


def get_user_contributions(user, total=10, wiki_url='https://meta.wikimedia.org'):
    """
    Get recent contributions for a user using public API (no OAuth needed).

    This function uses the public MediaWiki API to fetch user contributions.
    OAuth is not needed since contributions are publicly visible.

    Args:
        user: Django User object with social auth credentials
        total: Maximum number of contributions to retrieve (default: 10)
        wiki_url: Full URL to the wiki (default: 'https://meta.wikimedia.org')

    Returns:
        list: List of contribution dictionaries containing:
            - title: Page title
            - revid: Revision ID
            - timestamp: Timestamp of edit
            - comment: Edit summary
            - size: Size of the revision

    Example:
        >>> contribs = get_user_contributions(request.user, total=5)
        >>> for contrib in contribs:
        ...     print(f"{contrib['title']}: {contrib['comment']}")
    """
    # Get the Wikimedia username from social auth
    from social_django.models import UserSocialAuth
    try:
        social_auth = UserSocialAuth.objects.get(user=user, provider='mediawiki')
        username = social_auth.extra_data.get('username', user.username)
    except UserSocialAuth.DoesNotExist:
        username = user.username

    # Use public API (no OAuth) to get contributions
    from urllib.parse import urlparse
    import requests

    parsed = urlparse(wiki_url)
    api_url = f"{parsed.scheme}://{parsed.netloc}/w/api.php"

    params = {
        'action': 'query',
        'list': 'usercontribs',
        'ucuser': username,
        'uclimit': total,
        'ucprop': 'title|ids|timestamp|comment|size',
        'format': 'json'
    }

    response = requests.get(api_url, params=params)
    data = response.json()

    contributions = []
    if 'query' in data and 'usercontribs' in data['query']:
        for contrib in data['query']['usercontribs']:
            contributions.append({
                'title': contrib.get('title'),
                'revid': contrib.get('revid'),
                'timestamp': contrib.get('timestamp'),
                'comment': contrib.get('comment', ''),
                'size': contrib.get('size', 0)
            })

    return contributions


def make_edit_as_user(user, page_title, new_text, summary, wiki_url='https://meta.wikimedia.org'):
    """
    Make an edit to a wiki page using the user's OAuth credentials.

    Args:
        user: Django User object with social auth credentials
        page_title: Title of the page to edit
        new_text: New text content for the page
        summary: Edit summary
        wiki_url: Full URL to the wiki (default: 'https://meta.wikimedia.org')

    Returns:
        dict: Result containing:
            - success: True if edit was successful, False otherwise
            - error: Error message if unsuccessful (None if successful)
            - revid: Revision ID if successful

    Example:
        >>> result = make_edit_as_user(
        ...     request.user,
        ...     'User:Example/Sandbox',
        ...     'New content',
        ...     'Testing edit via OAuth'
        ... )
        >>> if result['success']:
        ...     print(f"Edit successful! Revision: {result['revid']}")
    """
    try:
        site = get_mwclient_for_user(user, wiki_url)
        page = site.pages[page_title]

        # Save the page with the new text
        result = page.save(new_text, summary=summary)

        return {
            'success': True,
            'error': None,
            'revid': result.get('newrevid')
        }
    except mwclient.errors.APIError as e:
        return {
            'success': False,
            'error': f"API Error: {e.code} - {e.info}",
            'revid': None
        }
    except Exception as e:
        return {
            'success': False,
            'error': f"Error making edit: {str(e)}",
            'revid': None
        }


def get_page_content(user, page_title, wiki_url='https://meta.wikimedia.org'):
    """
    Get the content of a wiki page using the user's OAuth credentials.

    Args:
        user: Django User object with social auth credentials
        page_title: Title of the page to retrieve
        wiki_url: Full URL to the wiki (default: 'https://meta.wikimedia.org')

    Returns:
        dict: Page information containing:
            - exists: True if page exists, False otherwise
            - text: Page content (wikitext)
            - revision: Current revision ID
            - length: Page length in bytes

    Example:
        >>> page_data = get_page_content(request.user, 'Main Page')
        >>> if page_data['exists']:
        ...     print(page_data['text'])
    """
    site = get_mwclient_for_user(user, wiki_url)
    page = site.pages[page_title]

    return {
        'exists': page.exists,
        'text': page.text() if page.exists else '',
        'revision': page.revision if page.exists else None,
        'length': page.length if page.exists else 0
    }
