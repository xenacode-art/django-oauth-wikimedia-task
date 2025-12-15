from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.translation import activate
from django.conf import settings
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
    """
    Vue-powered profile page that fetches data from API.
    """
    return render(request, 'user_profile/profile_vue.dtl')


def login_oauth(request):
    context = {}
    return render(request, 'user_profile/login.dtl', context)


def search(request):
    """
    Vue-powered search page for wiki replica database.
    """
    return render(request, 'user_profile/search_vue.dtl')


def statistics(request):
    """
    Vue-powered statistics dashboard showing wiki database stats.
    """
    return render(request, 'user_profile/statistics.dtl')


def profile_vue(request):
    """
    Vue-powered profile page that fetches data from API.
    """
    return render(request, 'user_profile/profile_vue.dtl')


def set_language(request):
    """
    Change the user's language preference.
    """
    if request.method == 'POST':
        language = request.POST.get('language')
        if language and language in dict(settings.LANGUAGES).keys():
            activate(language)
            response = redirect(request.POST.get('next', '/'))
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language)
            return response
    return redirect('/')
