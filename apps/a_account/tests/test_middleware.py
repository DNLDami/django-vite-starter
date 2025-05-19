import pytest
from django.http import HttpRequest, HttpResponse
from django.urls import reverse
from django.contrib.auth.models import AnonymousUser, User
from apps.a_account.middleware import CheckDeactivatedMiddleware


@pytest.mark.django_db
class TestCheckDeactivatedMiddleware:
    
    @pytest.fixture
    def get_response(self):
        """Mock get_response callable that returns a simple HttpResponse"""
        def _get_response(request):
            return HttpResponse('Normal Response')
        return _get_response
    
    @pytest.fixture(autouse=True)
    def setUp(self, request, client):
         # Skip fixture logic if test is marked with 'skip_autouse'
        if 'skip_autouse' in request.keywords:
            yield
            return
        self.active_user = User.objects.create_user(username='activeuser', password='pass')
        login_successful_active_user = client.login(username='activeuser', password='pass')
        assert login_successful_active_user
        self.inactive_user = User.objects.create_user(username='inactiveuser', password='pass')
        self.inactive_user.profile.is_active = False
        self.inactive_user.profile.save()
        login_successful_inactive_user = client.login(username='inactiveuser', password='pass')
        assert login_successful_inactive_user
        yield
        
    
    def test_active_user_passes_through(self, get_response):
        '''Test that users with active profile gets pass the middleware'''
        middleware = CheckDeactivatedMiddleware(get_response)
        request = HttpRequest()
        request.user = self.active_user
        request.path = reverse('home')

        response = middleware(request)

        assert response.status_code == 200
        assert response.content == b"Normal Response"
        
    def test_inactive_user_redirects(self, get_response):
        '''Test that users with inactive profile cannot get pass the middleware'''
        middleware = CheckDeactivatedMiddleware(get_response)
        request = HttpRequest()
        request.user = self.inactive_user
        activate_url = reverse('a_account:profile-activate-view')
        request.path = reverse('home')

        response = middleware(request)

        assert response.status_code == 302
        assert response.url == activate_url
        
    @pytest.mark.skip_autouse
    def test_unauthenticated_user_passes_through(self, get_response):
        '''Test that anonymous users gets pass the middleware'''
        middleware = CheckDeactivatedMiddleware(get_response)
        request = HttpRequest()
        request.user = AnonymousUser()
        request.path = reverse('home')

        response = middleware(request)

        assert response.status_code == 200
        assert response.content == b"Normal Response"
        
    def test_prevent_infinite_redirect_loop(self, get_response):
        middleware = CheckDeactivatedMiddleware(get_response)
        activate_url = reverse('a_account:profile-activate-view')
        request = HttpRequest()
        request.user = self.inactive_user
        request.path = activate_url  # Already on the activation page

        response = middleware(request)

        # Should not redirect again, should proceed normally
        assert response.status_code == 200
        assert response.content == b"Normal Response"