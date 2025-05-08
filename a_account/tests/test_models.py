import pytest 
from django.contrib.auth.models import User
from a_account.models import Profile
from django.templatetags.static import static
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.mark.django_db
class TestProfileModel:
    
    @pytest.fixture(autouse=True)
    def setUp(self):
        self.user = User.objects.create_user('testuser', password='password123')
        self.profile = Profile.objects.create(user=self.user)
    
    def test_name_property_with_diplayname_and_without_displayname(self):
        '''Tests that the name property is username when displayname is not given and profile obj returns username'''
        # profile without displyname
        assert str(self.profile) == 'testuser'
        assert self.profile.name == 'testuser'
        # profile with dispalyname
        self.profile.displayname = 'myname'
        self.profile.save()
        assert self.profile.name == 'myname'
        
    
    def test_profile_avatar_property_with_image_and_without_image(self):
        '''Test that the avatar property returns the default avatar if no image is provided'''
        assert self.profile.avatar == static('images/avatar.svg')
        
        image_file = SimpleUploadedFile(name='test_avatar.jpg', content=b'', content_type='image/jpeg')
        self.profile.image = image_file
        self.profile.save()
        assert self.profile.avatar == self.profile.image.url
        