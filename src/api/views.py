from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from social_django.models import UserSocialAuth
from user_profile.mwclient_utils import get_user_info, get_user_contributions
from wiki_replica.models import Page, RecentChanges
from .serializers import (
    UserProfileSerializer,
    ContributionSerializer,
    WikiPageSerializer,
    WikiStatisticsSerializer
)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    Get authenticated user's profile information including edit count and groups.
    """
    try:
        social_auth = UserSocialAuth.objects.get(
            user=request.user,
            provider='mediawiki'
        )

        try:
            user_info = get_user_info(request.user)
            data = {
                'username': user_info['name'],
                'edit_count': user_info['editcount'],
                'groups': user_info['groups'],
                'has_oauth': True
            }
        except Exception as e:
            data = {
                'username': request.user.username,
                'edit_count': 0,
                'groups': [],
                'has_oauth': True
            }

        serializer = UserProfileSerializer(data)
        return Response(serializer.data)

    except UserSocialAuth.DoesNotExist:
        return Response(
            {'error': 'User has no OAuth credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_contributions(request):
    """
    Get authenticated user's recent contributions.
    Query parameters:
    - limit: Number of contributions to return (default: 10, max: 50)
    """
    limit = min(int(request.GET.get('limit', 10)), 50)

    try:
        contributions = get_user_contributions(request.user, total=limit)
        serializer = ContributionSerializer(contributions, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def wiki_search(request):
    """
    Search wiki pages by title.
    Query parameters:
    - q: Search query
    - namespace: Namespace to search in (default: 0)
    - limit: Number of results (default: 20, max: 100)
    """
    query = request.GET.get('q', '').strip()
    namespace = int(request.GET.get('namespace', 0))
    limit = min(int(request.GET.get('limit', 20)), 100)

    if not query:
        return Response(
            {'error': 'Search query is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        search_term = query.replace(' ', '_')
        results = Page.objects.filter(
            page_namespace=namespace,
            page_title__icontains=search_term
        ).order_by('page_title')[:limit]

        serializer = WikiPageSerializer(results, many=True)
        return Response({
            'query': query,
            'namespace': namespace,
            'count': len(serializer.data),
            'results': serializer.data
        })
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def wiki_statistics(request):
    """
    Get wiki database statistics including page counts and recent changes.
    """
    try:
        total_pages = Page.objects.count()
        content_pages = Page.objects.filter(
            page_namespace=0,
            page_is_redirect=False
        ).count()
        redirects = Page.objects.filter(page_is_redirect=True).count()

        try:
            recent_changes_count = RecentChanges.objects.count()
        except Exception:
            recent_changes_count = 0

        data = {
            'total_pages': total_pages,
            'content_pages': content_pages,
            'redirects': redirects,
            'recent_changes_count': recent_changes_count
        }

        serializer = WikiStatisticsSerializer(data)
        return Response(serializer.data)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
