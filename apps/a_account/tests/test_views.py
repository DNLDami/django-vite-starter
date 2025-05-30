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
from django.contrib.messages import get_messages
from apps.a_account.models import Profile


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
        # Ensure profile is active to avoid middleware redirects
        self.user.profile.is_active = True
        self.user.profile.save()
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

@pytest.mark.django_db        
class TestProfileSettingsView:
    
    @pytest.fixture(autouse=True)
    def setUp(self, client):
        self.user = User.objects.create_user(username='testuser', password='password123',email='test@email.com')
        self.login_successful = client.login(username='testuser', password='password123')
        assert self.login_successful
        self.emailchange_url = reverse('a_account:profile-emailchange')
        self.username_edit_url = reverse('a_account:profile-username-edit')
        
    def test_get_request_to_emailchange_url_returns_htmx_form(self, client):
        '''Test that htmx form is rendered on the page when a get request is sent to 'profile-emailchange' url'''
        # Simulate HTMX request by adding 'HX-Request' header
        response = client.get(self.emailchange_url, HTTP_HX_REQUEST='true')
        assertTemplateUsed(response, 'partials/email_form.html')
        assert 'form' in response.context
    
    def test_email_is_updated_when_submitting_valid_form(self, mocker, client):
        '''Test that email field is updated when user submits a valid form and confirrmation email is sent'''
        mock_send_mail = mocker.patch('apps.a_account.views.send_email_confirmation')
        new_email = 'newtest@email.com'
        response = client.post(self.emailchange_url, data={'email':new_email})
        # should redirect on success 
        assertRedirects(response, expected_url=reverse('a_account:profile-settings'))
        self.user.refresh_from_db()
        assert self.user.email == new_email
        # send_email_confirmation should be sent once
        mock_send_mail.assert_called_once_with(response.wsgi_request, self.user)
        
    def test_settings_page_is_rerendered_with_errors_when_submitting_invalid_email_form(self, client, mocker):
        '''Test that profile settings page is rerendered when an invalid form is submitted and the error message is displayed also in the page and confirmation email is not sent'''
        mock_send_mail = mocker.patch('apps.a_account.views.send_email_confirmation')
        # submit an invalid form
        response = client.post(self.emailchange_url, data={'email':'invalid-email'})
        assert response.status_code == 200
        # should render profile_settings.html with form error
        assertTemplateUsed(response, 'a_account/profile_settings.html')
        form = response.context.get('email_form')
        assert form is not None
        assert form.errors
        mock_send_mail.assert_not_called()
        
    def test_other_request_method_to_emailchange_url_redirects_to_home(self, client):
        response = client.put(self.emailchange_url)
        assertRedirects(response, expected_url=reverse('home'))
        
    def test_get_request_to_username_edit_url_returns_htmx_form(self, client):
        '''Test that htmx form is rendered on the page when a get request is sent to username edit url'''
        # Simulate HTMX request by adding 'HX-Request' header
        response = client.get(self.username_edit_url, HTTP_HX_REQUEST='true')
        assertTemplateUsed(response, 'partials/username_form.html')
        assert 'form' in response.context
        
    def test_username_is_updated_when_submitting_valid_form(self, client):
        '''Test that username field is updated when user submits a valid form '''
        new_username = 'newtestuser'
        response = client.post(self.username_edit_url, data={'username':new_username})
        # should redirect on success 
        assertRedirects(response, expected_url=reverse('a_account:profile-settings'))
        self.user.refresh_from_db()
        assert self.user.username == new_username
    
    def test_settings_page_is_rerendered_with_errors_when_submitting_invalid_username_form(self, client):
        '''Test that profile settings page is rerendered when an invalid username form is submitted and the error message is displayed also in the page '''
        # submit an invalid form
        response = client.post(self.username_edit_url, data={'username':'invalid-username'})
        assert response.status_code == 200
        # should render profile_settings.html with form error
        assertTemplateUsed(response, 'a_account/profile_settings.html')
        form = response.context.get('username_form')
        assert form is not None
        assert 'username' in form.errors
    
    def test_other_request_method_to_username_edit_url_redirects_to_home(self, client):
        response = client.put(self.username_edit_url)
        assertRedirects(response, expected_url=reverse('home'))
        

@pytest.mark.django_db
class TestProfileEmailVerifyView:
    
    def test_email_verify_mail_is_sent_for_authenticated_users(self, client, mocker):
        '''Test email verify mail is sent when request is sent by an authenticated user'''
        mock_send_mail = mocker.patch('apps.a_account.views.send_email_confirmation')
        user = User.objects.create_user(username='testuser', password='password123')
        login_successful = client.login(username='testuser', password='password123')
        assert login_successful
        response = client.get(reverse('a_account:profile-emailverify'))
        mock_send_mail.assert_called_once_with(response.wsgi_request, user)
        
    def test_profile_email_verify_view_redirects_for_anonymous_users(self, client):
        '''Test that unauthenticated users are redirected to login page'''
        response = client.get(reverse('a_account:profile-emailverify'))
        assertRedirects(response, expected_url=f'{reverse('account_login')}?next={reverse('a_account:profile-emailverify')}')
        

@pytest.mark.django_db
class TestProfileActiveView:
    
    @pytest.fixture(autouse=True)
    def setUp(self, request, client):
        # Skip fixture logic if test is marked with 'skip_autouse'
        if 'skip_autouse' in request.keywords:
            yield
            return
        self.user = User.objects.create_user(username='testuser', password='password123')
        login_successful = client.login(username='testuser', password='password123')
        assert login_successful
        yield
    
    @pytest.mark.skip_autouse
    def test_profile_active_view_redirects_for_anonymous_users(self, client):
        '''Test that unauthenticated users are redirected to login page'''
        response = client.get(reverse('a_account:profile-deactivate-view'))
        assertRedirects(response, expected_url=f'{reverse('account_login')}?next={reverse('a_account:profile-deactivate-view')}')
        response = client.get(reverse('a_account:profile-activate-view'))
        assertRedirects(response, expected_url=f'{reverse('account_login')}?next={reverse('a_account:profile-activate-view')}')
        
    def test_profile_is_deactivated_and_reactivated_for_authenticated_users(self, client):
        '''
        Test that when an authenticated user sends a post request to 
        profile-deactivate-view the user account is deactivated and when 
        an authenticated user sends a post request to profile-activate-view
        '''
        # account deactivation
        response = client.post(reverse('a_account:profile-deactivate-view'))
        # assert user account is deactivated
        self.user.refresh_from_db()
        assert not self.user.profile.is_active
        assertRedirects(response, reverse('home'))
        # Check messages
        messages = list(get_messages(response.wsgi_request))
        assert str(messages[0]) == 'Account deactivated'
        # Verify logout
        assert '_auth_user_id' not in client.session
        
        # account reactivation
        login_successful = client.login(username='testuser', password='password123')
        assert login_successful
        # all requests ahould be redirected to the profile activation page
        response = client.get(reverse('home'))
        assertRedirects(response, expected_url=reverse('a_account:profile-activate-view'))
        
        response = client.post(reverse('a_account:profile-activate-view'))
        # assert user account is reactivated
        self.user.refresh_from_db()
        assert self.user.profile.is_active
        assertRedirects(response, reverse('home'))
        # Check messages
        messages = list(get_messages(response.wsgi_request))
        assert str(messages[0]) == 'Account reactivated'
        # Verify login
        assert '_auth_user_id' in client.session
        
    def test_get_request_returns_template(self, client):
        '''
        Test that when a get request is sent to the profile deactivate view 
        it returns the view's template
        '''
        response = client.get(reverse('a_account:profile-deactivate-view'))
        assert response.status_code == 200
        assertTemplateUsed(response, 'a_account/profile_deactivate.html')
    
    def test_active_profile_is_redirected_to_home(self, client):
        '''
        Test that when a user with an active profile sends a request to 
        profile-activate-view they are redirected to home
        '''
        response = client.post(reverse('a_account:profile-activate-view'))
        assertRedirects(response, reverse('home'))
    
    