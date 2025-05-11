from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.a_account.forms import ProfileForm
from django.urls import reverse
from django.contrib.auth.models import User


@login_required
def profile_view(request, username=None):
    if username:
        profile = get_object_or_404(User, username=username).profile
    else:
        try:
            profile = request.user.profile
        except:
            return redirect('account_login')
    return render(request, 'a_account\profile.html', {'profile':profile})


@login_required
def profile_edit_view(request):
    form = ProfileForm(instance=request.user.profile)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('profile-view')
        
    if request.path == reverse('profile-onboarding'):
        onboarding = True
    else:
        onboarding = False
    
    context = {
        'form':form,
        'onboarding':onboarding,
    }
    return render(request, 'a_account/profile_edit.html', context)

@login_required
def profile_settings_view(request):
    return render(request, 'a_account/profile_settings.html')
