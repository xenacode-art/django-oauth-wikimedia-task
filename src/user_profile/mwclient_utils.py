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
    Get user information including edit count using OAuth credentials.

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
    site = get_mwclient_for_user(user, wiki_url)

    # Query the API for user info
    result = site.api('query', meta='userinfo', uiprop='editcount|registration|groups')
    user_info = result['query']['userinfo']

    return {
        'name': user_info.get('name'),
        'editcount': user_info.get('editcount', 0),
        'registration': user_info.get('registration'),
        'groups': user_info.get('groups', [])
    }


def get_user_contributions(user, total=10, wiki_url='https://meta.wikimedia.org'):
    """
    Get recent contributions for a user using their OAuth credentials.

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
    site = get_mwclient_for_user(user, wiki_url)

    # Get authenticated user's username
    user_info = site.api('query', meta='userinfo')
    username = user_info['query']['userinfo']['name']

    # Query user contributions
    result = site.api(
        'query',
        list='usercontribs',
        ucuser=username,
        uclimit=total,
        ucprop='title|ids|timestamp|comment|size'
    )

    contributions = []
    for contrib in result['query']['usercontribs']:
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
