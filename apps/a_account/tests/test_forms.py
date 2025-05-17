import pytest 
from apps.a_account.forms import ProfileForm, EmailForm, UsernameForm
from django.urls import reverse
from django.contrib.auth.models import User
from django import forms

@pytest.mark.django_db
class TestProfileform:
    pass

@pytest.mark.django_db
class TestEmailForm:
    
    @pytest.mark.parametrize(
        'email, instance_id, expected_error',
        [
            ('new@email.com', None, None), # new email no errors
            ('invalid-email@email.com', None, "Email must contain only letters and digits, with a single '@' symbol."), # invalid email error is raised
            ('test@email.com', None, 'Email test@email.com is not available'), # existing email no instance id
            ('test@email.com', 1, None), # existing email and same instance id no errors
        ]
    )
    def test_email_form(self, email, instance_id, expected_error):
        '''
        Test that email field when new valid email is submitted,
        raises an error when existing email is submitted and
        user submitting is own email is passed
        '''
        # set up test database with a user
        if 'test@email.com' == email or instance_id == 1:
            User.objects.create(id=1, username='testuser', email=email)
        form = EmailForm(data={'email':email})
        # set the instance if needed
        form.instance = User.objects.get(id=instance_id) if instance_id else User()
        if expected_error:
            # form should be invalid
            assert not form.is_valid()
            assert 'email' in form.errors
            assert expected_error == form.errors['email'][0]
        else:
            # form should be valid
            assert form.is_valid()
            assert form.clean_email() == email

@pytest.mark.django_db            
class TestUsernameForm:
    
    @pytest.mark.parametrize(
        'username, instance_id, expected_error',
        [
            ('newusername', None, None), # new username no errors
            ('invalid-username', None, 'Username can only contain letters, digits, and underscores.'), # invalid username error is raised
            ('testusername', None, 'Username @testusername is not available'), # existing username no instance id
            ('testusername', 1, None), # existing username and same instance id no errors
        ]
    )
    def test_username_for(self, username, instance_id, expected_error):
        '''
        Test that username field when new valid email is submitted,
        raises an error when existing username is submitted and
        user submitting is own username is passed
        '''
        # set up test database with a user
        if 'testusername' == username or instance_id == 1:
            User.objects.create(id=1, username=username)
        form = UsernameForm(data={'username':username})
        # set the instance if needed
        form.instance = User.objects.get(id=instance_id) if instance_id else User()
        if expected_error:
            # form should be invalid
            assert not form.is_valid()
            assert 'username' in form.errors
            assert expected_error == form.errors['username'][0]
        else:
            assert form.is_valid()
            assert form.clean_username() == username