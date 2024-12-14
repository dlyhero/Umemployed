from django.contrib import admin
from django.urls import path, include,re_path

from django.conf import settings
from django.conf.urls.static import static
from users import views
from django.contrib.auth import views as auth_views
from users.views import CustomConfirmEmailView

from users.views import custom_404_view, custom_500_view
from allauth.account.views import confirm_email, email_verification_sent


# Define custom error handlers
handler404 = 'users.views.custom_404_view'
handler500 = 'users.views.custom_500_view'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/user/', include('users.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('jobs',views.home, name = 'home'),
    path('',views.index, name = 'index'),
    
    path('accounts/', include('allauth.urls')),
    path('social-auth/', include(('social_django.urls', 'social'), namespace='social')),
    
    #urls for the password reset with email
    path('reset_password/',auth_views.PasswordResetView.as_view(template_name='password_reset/passwordReset.html'),name='reset_password'),
    path('password_reset_done/',auth_views.PasswordResetDoneView.as_view(template_name='password_reset/passwordResetSent.html'), name ="password_reset_done"),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset/passwordResetForm.html'), name="password_reset_confirm"),
    path('password_reset_complete/',auth_views.PasswordResetCompleteView.as_view(template_name='password_reset/passwordResetDone.html'),name='password_reset_complete'),
   
    # for the company app
    path('company/', include('company.urls')),
    #for the resume app
    path('resume/', include('resume.urls')),
    path('job/',include('job.urls')),
    path('jobs/',include('website.urls')),
    path('onboarding/', include('onboarding.urls')),
    path('assessments/', include('asseessments.urls')),
    path('posts/',include('social_features.urls')),
    
    path('messages/',include('messaging.urls')),
    path('notifications/',include('notifications.urls')),
    
    re_path(r'^accounts/confirm-email/(?P<key>[-:\w]+)/$', confirm_email, name='account_confirm_email'),
    
    path('ckeditor/', include('ckeditor_uploader.urls')),
    
    path('resend_confirmation_email/', views.resend_confirmation_email, name='resend_confirmation_email'),
    
    path('accounts/verify-email/', confirm_email, name='verify_email'),
    path('accounts/email-verification-sent/', email_verification_sent, name='account_email_verification_sent'),

    path('accounts/resend-verification-email/', views.resend_verification_email, name='resend_verification_email'),
    #for video chat
    path('chat/', include('videochat.urls')),
    
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

