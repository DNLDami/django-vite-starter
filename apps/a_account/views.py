from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.a_account.forms import ProfileForm, EmailForm, UsernameForm
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import messages
from allauth.account.utils import send_email_confirmation
from django.contrib.auth import logout
from apps.a_account.models  import Profile


@login_required
def profile_view(request, username=None):
    if username:
        profile = get_object_or_404(User, username=username).profile
    else:
        profile = request.user.profile
        # try:
        #     profile = request.user.profile
        # except:
        #     return redirect('account_login')
    return render(request, 'a_account/profile.html', {'profile':profile})


@login_required
def profile_edit_view(request):
    form = ProfileForm(instance=request.user.profile)
    
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            return redirect('a_account:profile-view')
        
    if request.path == reverse('a_account:profile-onboarding'):
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
    if request.path == reverse('a_account:profile-emailchange'):
        if request.htmx:
            form = EmailForm(instance=request.user)
            return render(request, 'partials/email_form.html', {'form':form})
        
        if request.method == 'POST':
            form = EmailForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                # then signal updates email address and set verified to false on the all auth table
                # then send confirmation email
                send_email_confirmation(request, request.user)
                return redirect('a_account:profile-settings')
            else:
                return render(request, 'a_account/profile_settings.html', {'email_form':form})
        else:
            return redirect('home')
        
    if request.path == reverse('a_account:profile-username-edit'):
        if request.htmx:
            form = UsernameForm(instance=request.user)
            return render(request, 'partials/username_form.html', {'form':form})
        
        if request.method == 'POST':
            form = UsernameForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                return redirect('a_account:profile-settings')
            else:
                return render(request, 'a_account/profile_settings.html', {'username_form':form})
        else:
            return redirect('home')
        
    return render(request, 'a_account/profile_settings.html')


@login_required
def profile_email_verify(request):
    send_email_confirmation(request, request.user)
    return redirect('a_account:profile-settings')


@login_required
def profile_active_view(request):
    profile = get_object_or_404(Profile, pk=request.user.id)
    if request.path == reverse('a_account:profile-deactivate-view'):
        if request.method == 'POST':
            logout(request)
            profile.is_active = False
            profile.save()
            messages.success(request, 'Account deactivated')
            return redirect('home')
        else:
            return render(request, 'a_account/profile_deactivate.html')
        
    if request.path == reverse('a_account:profile-activate-view'):
        if profile.is_active:
            return redirect('home')
        if request.method == 'POST':
            profile.is_active = True
            profile.save()
            messages.success(request, 'Account reactivated')
            return redirect('home')
        else:
            return render(request, 'a_account/profile_activate.html')