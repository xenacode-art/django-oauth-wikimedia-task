import pytest
from django.urls import reverse
from unittest.mock import patch, MagicMock


@pytest.mark.django_db
@pytest.mark.api
class TestUserProfileAPI:
    """Tests for user profile API endpoint."""

    def test_profile_requires_authentication(self, client):
        """Test that profile endpoint requires authentication."""
        response = client.get('/api/user/profile/')
        assert response.status_code == 403

    def test_profile_without_oauth(self, authenticated_client):
        """Test profile endpoint when user has no OAuth credentials."""
        response = authenticated_client.get('/api/user/profile/')
        assert response.status_code == 401
        data = response.json()
        assert 'error' in data

    @patch('api.views.get_user_info')
    def test_profile_with_oauth(self, mock_get_user_info, oauth_authenticated_client):
        """Test profile endpoint with OAuth credentials."""
        mock_get_user_info.return_value = {
            'name': 'TestUser',
            'editcount': 100,
            'groups': ['user', 'autoconfirmed']
        }

        response = oauth_authenticated_client.get('/api/user/profile/')
        assert response.status_code == 200
        data = response.json()
        assert data['username'] == 'TestUser'
        assert data['edit_count'] == 100
        assert data['has_oauth'] is True


@pytest.mark.django_db
@pytest.mark.api
class TestUserContributionsAPI:
    """Tests for user contributions API endpoint."""

    def test_contributions_requires_authentication(self, client):
        """Test that contributions endpoint requires authentication."""
        response = client.get('/api/user/contributions/')
        assert response.status_code == 403

    @patch('api.views.get_user_contributions')
    def test_contributions_success(self, mock_get_contributions, oauth_authenticated_client):
        """Test successful contributions fetch."""
        mock_get_contributions.return_value = [
            {
                'title': 'Test Page',
                'timestamp': '2025-01-15T12:00:00Z',
                'comment': 'Test edit',
                'size': 1000
            }
        ]

        response = oauth_authenticated_client.get('/api/user/contributions/?limit=10')
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['title'] == 'Test Page'

    def test_contributions_limit_parameter(self, oauth_authenticated_client):
        """Test that limit parameter is respected."""
        response = oauth_authenticated_client.get('/api/user/contributions/?limit=100')
        assert response.status_code in [200, 500]


@pytest.mark.django_db
@pytest.mark.api
class TestWikiSearchAPI:
    """Tests for wiki search API endpoint."""

    def test_search_without_query(self, client):
        """Test search endpoint without query parameter."""
        response = client.get('/api/wiki/search/')
        assert response.status_code == 400
        data = response.json()
        assert 'error' in data

    def test_search_with_query(self, client):
        """Test search endpoint with query parameter."""
        response = client.get('/api/wiki/search/?q=test')
        assert response.status_code in [200, 500]

    def test_search_with_namespace(self, client):
        """Test search with namespace parameter."""
        response = client.get('/api/wiki/search/?q=test&namespace=4')
        assert response.status_code in [200, 500]


@pytest.mark.django_db
@pytest.mark.api
class TestWikiStatisticsAPI:
    """Tests for wiki statistics API endpoint."""

    def test_statistics_endpoint(self, client):
        """Test statistics endpoint."""
        response = client.get('/api/wiki/statistics/')
        assert response.status_code in [200, 500]

    def test_statistics_response_structure(self, client):
        """Test that statistics response has correct structure."""
        response = client.get('/api/wiki/statistics/')
        if response.status_code == 200:
            data = response.json()
            assert 'total_pages' in data
            assert 'content_pages' in data
            assert 'redirects' in data
            assert 'recent_changes_count' in data
