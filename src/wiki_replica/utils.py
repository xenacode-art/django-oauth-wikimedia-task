"""
Utility functions for querying wiki replica database.

These functions provide convenient access to wiki data through
Django ORM models mapped to MediaWiki database tables.
"""

from .models import Page, Revision, Actor, User, RecentChanges, Logging


def get_recent_changes(limit=10):
    """
    Get recent changes from the wiki.

    Args:
        limit: Maximum number of recent changes to retrieve

    Returns:
        QuerySet of RecentChanges objects
    """
    return RecentChanges.objects.all().order_by('-rc_timestamp')[:limit]


def get_page_by_title(title, namespace=0):
    """
    Get a page by its title and namespace.

    Args:
        title: Page title
        namespace: Namespace ID (default: 0 for main namespace)

    Returns:
        Page object or None
    """
    try:
        return Page.objects.get(page_title=title, page_namespace=namespace)
    except Page.DoesNotExist:
        return None


def get_page_revisions(page_id, limit=10):
    """
    Get revisions for a specific page.

    Args:
        page_id: The page ID
        limit: Maximum number of revisions to retrieve

    Returns:
        QuerySet of Revision objects
    """
    return Revision.objects.filter(
        rev_page=page_id
    ).order_by('-rev_timestamp')[:limit]


def get_user_by_name(username):
    """
    Get a user by their username.

    Args:
        username: The username to search for

    Returns:
        User object or None
    """
    try:
        return User.objects.get(user_name=username)
    except User.DoesNotExist:
        return None


def get_user_edit_count_from_db(username):
    """
    Get edit count for a user from the wiki database.

    Args:
        username: The username

    Returns:
        int: Edit count or None if user not found
    """
    user = get_user_by_name(username)
    if user:
        return user.user_editcount
    return None


def get_namespace_pages(namespace=0, limit=100):
    """
    Get pages from a specific namespace.

    Args:
        namespace: Namespace ID
        limit: Maximum number of pages to retrieve

    Returns:
        QuerySet of Page objects
    """
    return Page.objects.filter(
        page_namespace=namespace
    ).order_by('-page_touched')[:limit]


def search_pages(search_term, namespace=0, limit=20):
    """
    Search for pages by title (simple LIKE search).

    Args:
        search_term: Search string
        namespace: Namespace ID to search in
        limit: Maximum results

    Returns:
        QuerySet of Page objects
    """
    return Page.objects.filter(
        page_title__icontains=search_term,
        page_namespace=namespace
    )[:limit]


def get_log_entries(log_type=None, limit=10):
    """
    Get log entries, optionally filtered by type.

    Args:
        log_type: Type of log entries (e.g., 'delete', 'block', 'upload')
        limit: Maximum number of entries

    Returns:
        QuerySet of Logging objects
    """
    queryset = Logging.objects.all()

    if log_type:
        queryset = queryset.filter(log_type=log_type)

    return queryset.order_by('-log_timestamp')[:limit]


def get_actor_by_name(actor_name):
    """
    Get an actor by name.

    Args:
        actor_name: The actor's name

    Returns:
        Actor object or None
    """
    try:
        return Actor.objects.get(actor_name=actor_name)
    except Actor.DoesNotExist:
        return None


def get_page_statistics():
    """
    Get basic statistics about pages in the wiki.

    Returns:
        dict: Statistics including total pages, redirects, etc.
    """
    total_pages = Page.objects.count()
    redirects = Page.objects.filter(page_is_redirect=True).count()
    new_pages = Page.objects.filter(page_is_new=True).count()

    return {
        'total_pages': total_pages,
        'redirects': redirects,
        'new_pages': new_pages,
        'content_pages': total_pages - redirects,
    }
