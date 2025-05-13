import pytest 
from django.contrib.auth.models import User
from apps.a_account.models import Profile
from allauth.account.models import EmailAddress


@pytest.mark.django_db
class TestUserSignal:
    
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password123', email='test@testmail.com')
        
    
    def test_new_profile_is_created_when_user_is_created(self):
        '''Test that a new profile table is created when a new user is created'''
        assert Profile.objects.filter(user=self.user).exists()
        profile = self.user.profile
        assert profile.user == self.user
    
    def test_new_profile_is_not_created_on_user_update(self):
        '''Test that a new profile table is not created when user is updated'''
        profile_count = Profile.objects.count()
        self.user.username = 'testuserupdated'
        self.user.save()
        assert Profile.objects.count() == profile_count
        
    def test_allauth_email_address_is_updated_on_email_edit(self):
        '''Test that allauth email address table is created on user creation and is updated when user email field is changes'''
        # email address should be created and linked 
        try:
            email_address = EmailAddress.objects.get_primary(self.user)
        except EmailAddress.DoesNotExist:
            email_address = None
        assert email_address is not None
        assert email_address.email == self.user.email
        assert email_address.verified == False
        
        # when user email is changed EmailAddress should be updated and unverified
        self.user.email = 'newemail@testmail.com'
        self.user.save()
        email_address.refresh_from_db()
        assert email_address.email == 'newemail@testmail.com'
        assert email_address.verified == False
    
    def test_username_lowercased_on_save(self):
        '''Test that username and email is always on lowercase'''
        self.user.username = 'UPPERCASE'
        self.user.email = 'UPPERCASE@EMAIL.COM'
        self.user.save()
        assert self.user.username == 'uppercase'
        assert self.user.email == 'uppercase@email.com'
        
        # updates with mixed case
        self.user.username = 'MixEDcaSE'
        self.user.email = 'MixEDcaSE@EmAIl.Com'
        self.user.save()
        self.user.refresh_from_db()
        assert self.user.username == 'mixedcase'
        assert self.user.email == 'mixedcase@email.com'
        
        
        