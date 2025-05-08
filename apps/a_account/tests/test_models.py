import pytest 
from django.contrib.auth.models import User
from apps.a_account.models import Profile
from django.templatetags.static import static
from django.core.files.uploadedfile import SimpleUploadedFile
import shutil
import tempfile
import os
from django.conf import settings

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
        