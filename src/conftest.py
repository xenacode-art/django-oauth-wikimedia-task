import pytest
from django.contrib.auth.models import User
from social_django.models import UserSocialAuth


@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def user_with_oauth(db, user):
    """Create a test user with OAuth credentials."""
    UserSocialAuth.objects.create(
        user=user,
        provider='mediawiki',
        uid='12345',
        extra_data={
            'access_token': {
                'oauth_token': 'test_token',
                'oauth_token_secret': 'test_secret'
            }
        }
    )
    return user


@pytest.fixture
def authenticated_client(client, user):
    """Create an authenticated client."""
    client.force_login(user)
    return client


@pytest.fixture
def oauth_authenticated_client(client, user_with_oauth):
    """Create an authenticated client with OAuth credentials."""
    client.force_login(user_with_oauth)
    return client
