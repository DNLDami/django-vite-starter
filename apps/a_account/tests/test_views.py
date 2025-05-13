import pytest 
from pytest_django.asserts import assertTemplateUsed, assertContains, assertRedirects
from django.urls import reverse

class TestProfileView:
    def test_profile_view_redirects_for_anonymous_users(self, client):
        '''Test that unauthenticated users are redirected to login page'''
        pass
        # response = client.get(reverse('profile-view'))
        # assertRedirects(response, expected_url=f'{reverse('login')}?next={reverse('profile')}')

    
    def test_profile_view_available_for_authenticated_users(self, client):
        '''Test that authenticated users can view profile page'''
        pass
    
    def test_profile_views_used_correct_html(self, client):
        '''Tests that the profile view returns correct html'''
        pass
        # response = client.get(reverse('profile-view'))
        # assertTemplateUsed(response, 'profile.html')