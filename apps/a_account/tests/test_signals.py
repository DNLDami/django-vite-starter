import pytest 
from django.contrib.auth.models import User
from apps.a_account.models import Profile


@pytest.mark.django_db
class TestUserSignal:
    
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.user = User.objects.create_user('testuser', 'password123')
        
    
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
        