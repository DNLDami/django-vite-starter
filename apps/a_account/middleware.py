from django.shortcuts import redirect
from django.urls import reverse

class CheckDeactivatedMiddleware:
    '''
    This middleware checks the user profile is_active field,
    if it's True the website content is rendered normally
    and if it's False the profile_activation_view is called
    '''
    def __init__(self, get_response):
        self.get_response = get_response
        
    def __call__(self, request):
        # Avoid infinte redirect loop
        if request.user.is_authenticated:
            profile = getattr(request.user, 'profile', None)
            activate_url = reverse('a_account:profile-activate-view')
            if profile and not profile.is_active and request.path != activate_url:
                return redirect(activate_url)
        return self.get_response(request)