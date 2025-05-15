import pytest 
from pytest_django.asserts import assertTemplateUsed, assertContains, assertRedirects
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
import shutil
import tempfile
import os
from io import BytesIO
from PIL import Image


@pytest.mark.django_db
class TestProfileView:
    
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.user2 = User.objects.create_user(username='testuser2', password='password123')
    
    def test_profile_view_redirects_for_anonymous_users(self, client):
        '''Test that unauthenticated users are redirected to login page'''
        response = client.get(reverse('a_account:profile-view'))
        assertRedirects(response, expected_url=f'{reverse('account_login')}?next={reverse('a_account:profile-view')}')

    
    def test_profile_view_available_for_authenticated_users(self, client):
        '''Test that authenticated users can view profile page'''
        login_successful = client.login(username=self.user.username, password='password123')
        assert login_successful
        response = client.get(reverse('a_account:profile-view'))
        assertContains(response, self.user.username, status_code=200)
        assertTemplateUsed(response, 'a_account/profile.html')
        
    def test_logged_in_users_can_view_other_profile(self, client):
        login_successful = client.login(username=self.user.username, password='password123')
        assert login_successful
        response = client.get(reverse('a_account:profile', args=[self.user2.username]))
        assertContains(response, self.user2.username, status_code=200)
        assertTemplateUsed(response, 'a_account/profile.html')
        


@pytest.fixture(autouse=True)
def temp_media_root(settings):
    # Create a temporary directory for MEDIA_ROOT
    temp_dir = tempfile.mkdtemp()
    settings.MEDIA_ROOT = temp_dir  # Override MEDIA_ROOT for tests

    yield  # Run the test

    # Cleanup: remove the entire temporary MEDIA_ROOT directory after test
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
        
@pytest.mark.django_db
@pytest.mark.usefixtures('temp_media_root')
class TestProfileEditView:
    
    @pytest.fixture(autouse=True)  
    def setUo(self):
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.profile_edit_url = reverse('a_account:profile-edit-view')
        self.profile_onboarding_url = reverse('a_account:profile-onboarding')
        
    def test_profile_view_redirects_for_anonymous_users(self, client):
        '''Test that unauthenticated users are redirected to login page'''
        response = client.get(reverse('a_account:profile-view'))
        assertRedirects(response, expected_url=f'{reverse('account_login')}?next={reverse('a_account:profile-view')}')
        
    def test_renders_form_for_authenticated_users(self, client):
        '''Test that profile edit form is rendered or displayed or visible for authenticated users'''
        login_successful = client.login(username=self.user.username, password='password123')
        assert login_successful
        response = client.get(self.profile_edit_url)
        assert response.status_code == 200
        assert 'form' in response.context
        assert response.context['onboarding'] is False
        assertTemplateUsed(response, 'a_account/profile_edit.html')
        
    def test_update_profile_when_submitting_valid_form_and_redirects_to_profile_view(self, client):
        '''Test that profile is updated when the form is submitted with valid data and user is redirected to profile view'''
        login_successful = client.login(username=self.user.username, password='password123')
        assert login_successful
        
        # Create a simple image using Pillow
        image = Image.new('RGB', size=(100, 100), color=(155, 0, 0))
        byte_io = BytesIO()
        image.save(byte_io, format='JPEG')
        byte_io.seek(0)
        image_file = SimpleUploadedFile(name='test_avatar.jpg', content=byte_io.read(), content_type='image/jpeg') 
        
        profile_form_data = {
            'image': image_file,
            'displayname': 'Test User',
            'info': 'The test user'
        }
        response = client.post(self.profile_edit_url, data=profile_form_data)
        assertRedirects(response, reverse('a_account:profile-view'))
        # Reload profile from DB and check changes
        self.user.profile.refresh_from_db()
        assert 'test_avatar' in self.user.profile.image.name
        assert self.user.profile.image.name.endswith('.jpg')
        assert self.user.profile.displayname == 'Test User'
        assert self.user.profile.info == 'The test user'
        
    def test_onboarding_flag_works_correctly(self, client):
        login_successful = client.login(username=self.user.username, password='password123')
        assert login_successful
        response = client.get(self.profile_onboarding_url)
        assert response.status_code == 200
        assert response.context['onboarding'] is True