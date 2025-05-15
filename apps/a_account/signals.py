from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.contrib.auth.models import User
from apps.a_account.models import Profile
from allauth.account.models import EmailAddress

@receiver(post_save, sender=User)
def create_profile_on_user_created(sender, instance, created, **kwargs):
    user = instance
    
    # add profile if user is created
    if created:
        Profile.objects.create(
            user=user
        )
        EmailAddress.objects.create(
            user = user,
            email = user.email,
            primary = True,
            verified = False
        )
    else:
        try:
            email_address = EmailAddress.objects.get_primary(user)
            if email_address.email != user.email:
                email_address.email = user.email
                email_address.verified = False
                email_address.save()
        except:
            # if allauth email address doesn't exist create one
            EmailAddress.objects.create(
                user = user,
                email = user.email,
                primary = True,
                verified = False
            )
        
@receiver(pre_save, sender=User)
def username_and_email_to_lowercase_on_save(sender, instance, **kwargs):
    instance.username = instance.username.lower()
    if instance.email:
        instance.email = instance.email.lower()