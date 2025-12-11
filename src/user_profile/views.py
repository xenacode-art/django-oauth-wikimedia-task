from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .pywikibot_utils import get_user_edit_count, get_user_contributions
from social_django.models import UserSocialAuth


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

        # Optionally fetch edit count and contributions
        # Uncomment these lines when you want to use Pywikibot features
        # Note: This requires proper Pywikibot configuration
        # try:
        #     context['edit_count'] = get_user_edit_count(request.user)
        #     context['contributions'] = get_user_contributions(request.user, total=5)
        # except Exception as e:
        #     context['pywikibot_error'] = str(e)

    except UserSocialAuth.DoesNotExist:
        context['has_oauth'] = False

    return render(request, 'user_profile/profile.dtl', context)


def login_oauth(request):
    context = {}
    return render(request, 'user_profile/login.dtl', context)
