"""
Utility functions for integrating Pywikibot with Django OAuth credentials.

This module provides functions to create Pywikibot instances using
OAuth credentials from Django's social-auth session.

⚠️ WARNING: MULTI-USER LIMITATION ⚠️
Pywikibot caches credentials globally, which causes issues in multi-user
web applications where multiple users are authenticated simultaneously.

PROBLEM:
- When User A logs in, Pywikibot caches their OAuth credentials
- When User B logs in, Pywikibot may still use User A's cached credentials
- This causes authentication failures and wrong-user actions

SOLUTION FOR PRODUCTION:
Use mwclient_utils.py instead for OAuth-authenticated operations in web apps.
Pywikibot is great for single-user bots, but mwclient is designed for
concurrent multi-user environments.

This module is kept for:
- Learning purposes
- Single-user/testing scenarios
- Non-OAuth Pywikibot operations (like reading wiki replicas)

See: https://github.com/Wikimedia-Suomi/PendingChangesBot-ng discussions
Credit: Issue discovered by Zache during Outreachy internship
"""

import pywikibot
from pywikibot import Site
from social_django.models import UserSocialAuth


def get_pywikibot_site_for_user(user, wiki='meta', family='wikimedia'):
    """
    Get a Pywikibot Site instance authenticated with the user's OAuth credentials.

    Args:
        user: Django User object with social auth credentials
        wiki: Wiki code (default: 'meta')
        family: Wiki family (default: 'wikimedia')

    Returns:
        pywikibot.Site: Authenticated Pywikibot site instance

    Raises:
        UserSocialAuth.DoesNotExist: If user has no social auth credentials
        ValueError: If OAuth credentials are incomplete
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

    site = Site(wiki, family)

    site.login(oauth_token=oauth_token, oauth_token_secret=oauth_token_secret)

    return site


def get_user_edit_count(user, wiki='meta', family='wikimedia'):
    """
    Get the edit count for a user on a specific wiki using their OAuth credentials.

    Args:
        user: Django User object with social auth credentials
        wiki: Wiki code (default: 'meta')
        family: Wiki family (default: 'wikimedia')

    Returns:
        int: Number of edits by the user
    """
    site = get_pywikibot_site_for_user(user, wiki, family)
    pywikibot_user = pywikibot.User(site, user.username)
    return pywikibot_user.editCount()


def get_user_contributions(user, total=10, wiki='meta', family='wikimedia'):
    """
    Get recent contributions for a user using their OAuth credentials.

    Args:
        user: Django User object with social auth credentials
        total: Maximum number of contributions to retrieve (default: 10)
        wiki: Wiki code (default: 'meta')
        family: Wiki family (default: 'wikimedia')

    Returns:
        list: List of contribution dictionaries
    """
    site = get_pywikibot_site_for_user(user, wiki, family)
    pywikibot_user = pywikibot.User(site, user.username)

    contributions = []
    for contrib in pywikibot_user.contributions(total=total):
        contributions.append({
            'page': contrib[0].title(),
            'revid': contrib[1],
            'timestamp': contrib[2],
            'comment': contrib[3],
        })

    return contributions


def make_edit_as_user(user, page_title, new_text, summary, wiki='meta', family='wikimedia'):
    """
    Make an edit to a wiki page using the user's OAuth credentials.

    Args:
        user: Django User object with social auth credentials
        page_title: Title of the page to edit
        new_text: New text content for the page
        summary: Edit summary
        wiki: Wiki code (default: 'meta')
        family: Wiki family (default: 'wikimedia')

    Returns:
        bool: True if edit was successful, False otherwise
    """
    site = get_pywikibot_site_for_user(user, wiki, family)
    page = pywikibot.Page(site, page_title)

    try:
        page.text = new_text
        page.save(summary=summary)
        return True
    except Exception as e:
        print(f"Error making edit: {e}")
        return False
