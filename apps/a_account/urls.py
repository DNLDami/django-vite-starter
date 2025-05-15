from django.urls import path
from apps.a_account import views

app_name = 'a_account' 

urlpatterns = [
    path('', views.profile_view, name='profile-view'),
    path('@<username>', views.profile_view, name='profile'),
    path('edit/', views.profile_edit_view, name='profile-edit-view'),
    path('deactivate/', views.profile_deactivate_view, name='profile-deactivate-view'),
    path('onboarding/', views.profile_edit_view, name='profile-onboarding'),
    path('settings/', views.profile_settings_view, name='profile-settings'),
    path('emailchange/', views.profile_email_change, name='profile-emailchange'),
    path('emailverify/', views.profile_email_verify, name='profile-emailverify'),
]

