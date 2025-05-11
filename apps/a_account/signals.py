from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User
from apps.a_account.models import Profile

@receiver(post_save, sender=User)
def create_profile_on_user_created(sender, instance, created, **kwargs):
    user = instance
    
    # add profile if user is created
    if created:
        Profile.objects.create(
            user=user
        )
        
@receiver(pre_save, sender=User)
def username_to_lowercase_on_save(sender, instance, **kwargs):
    if instance.username:
        instance.username = instance.username.lower()