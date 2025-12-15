import pytest
from django.urls import reverse


@pytest.mark.django_db
@pytest.mark.unit
class TestIndexView:
    """Tests for index view."""

    def test_index_page_loads(self, client):
        """Test that index page loads successfully."""
        response = client.get('/')
        assert response.status_code == 200

    def test_index_uses_correct_template(self, client):
        """Test that index view uses correct template."""
        response = client.get('/')
        assert 'user_profile/index.dtl' in [t.name for t in response.templates]


@pytest.mark.django_db
@pytest.mark.unit
class TestProfileView:
    """Tests for profile view."""

    def test_profile_requires_login(self, client):
        """Test that profile requires authentication."""
        response = client.get('/profile')
        assert response.status_code == 302
        assert '/accounts/login' in response.url

    def test_profile_loads_for_authenticated_user(self, authenticated_client):
        """Test that profile loads for authenticated user."""
        response = authenticated_client.get('/profile')
        assert response.status_code == 200

    def test_profile_uses_vue_template(self, authenticated_client):
        """Test that profile uses Vue template."""
        response = authenticated_client.get('/profile')
        assert 'user_profile/profile_vue.dtl' in [t.name for t in response.templates]


@pytest.mark.django_db
@pytest.mark.unit
class TestSearchView:
    """Tests for search view."""

    def test_search_page_loads(self, client):
        """Test that search page loads successfully."""
        response = client.get('/search')
        assert response.status_code == 200

    def test_search_uses_vue_template(self, client):
        """Test that search uses Vue template."""
        response = client.get('/search')
        assert 'user_profile/search_vue.dtl' in [t.name for t in response.templates]


@pytest.mark.django_db
@pytest.mark.unit
class TestStatisticsView:
    """Tests for statistics view."""

    def test_statistics_page_loads(self, client):
        """Test that statistics page loads successfully."""
        response = client.get('/statistics')
        assert response.status_code == 200

    def test_statistics_uses_correct_template(self, client):
        """Test that statistics uses correct template."""
        response = client.get('/statistics')
        assert 'user_profile/statistics.dtl' in [t.name for t in response.templates]


@pytest.mark.django_db
@pytest.mark.unit
class TestLanguageSwitcher:
    """Tests for language switching functionality."""

    def test_set_language_redirects_without_post(self, client):
        """Test that set_language redirects on GET request."""
        response = client.get('/set-language')
        assert response.status_code == 302

    def test_set_language_changes_language(self, client):
        """Test that language can be changed."""
        response = client.post('/set-language', {
            'language': 'fi',
            'next': '/'
        })
        assert response.status_code == 302
        assert response.cookies.get('django_language').value == 'fi'

    def test_set_language_invalid_language(self, client):
        """Test that invalid language codes are ignored."""
        response = client.post('/set-language', {
            'language': 'xx',
            'next': '/'
        })
        assert response.status_code == 302
