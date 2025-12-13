from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from social_django.models import UserSocialAuth

# Use mwclient for production (thread-safe for multi-user apps)
from .mwclient_utils import get_user_info, get_user_contributions

# Pywikibot is kept for reference but has multi-user limitations
# from .pywikibot_utils import get_user_edit_count, get_user_contributions


def index(request):
    context = {}
    return render(request, 'user_profile/index.dtl', context)


@login_required()
def profile(request):
    context = {}

    # Check if user has OAuth credentials
    try:
        social_auth = UserSocialAuth.objects.get(user=request.user, provider='mediawiki')
        context['has_oauth'] = True

        # Fetch user info and contributions using mwclient (multi-user safe)
        try:
            # Get user information (includes edit count)
            user_info = get_user_info(request.user)
            context['edit_count'] = user_info['editcount']
            context['username'] = user_info['name']
            context['user_groups'] = user_info['groups']

            # Get recent contributions
            context['contributions'] = get_user_contributions(request.user, total=5)

        except Exception as e:
            context['api_error'] = str(e)
            # Set defaults if API call fails
            context['edit_count'] = 'N/A'
            context['username'] = request.user.username
            context['contributions'] = []

    except UserSocialAuth.DoesNotExist:
        context['has_oauth'] = False

    return render(request, 'user_profile/profile.dtl', context)


def login_oauth(request):
    context = {}
    return render(request, 'user_profile/login.dtl', context)


def search(request):
    """
    Search wiki replica database for pages by title.
    """
    from wiki_replica.models import Page
    from django.conf import settings
    import os

    context = {}

    # Get wiki name from environment or settings
    wiki_code = os.environ.get('WIKI_REPLICA', 'metawiki')
    context['wiki_name'] = wiki_code
    context['namespace'] = 0  # Main namespace

    query = request.GET.get('q', '').strip()
    context['query'] = query

    if query:
        # Search for pages in main namespace (0) containing the query string
        # Replace spaces with underscores (MediaWiki convention)
        search_term = query.replace(' ', '_')

        try:
            # Search for pages where title contains the search term
            results = Page.objects.filter(
                page_namespace=0,
                page_title__icontains=search_term
            ).order_by('page_title')[:50]  # Limit to 50 results

            context['results'] = results
        except Exception as e:
            # Handle database errors gracefully
            context['error'] = str(e)
            context['results'] = []

    return render(request, 'user_profile/search.dtl', context)
