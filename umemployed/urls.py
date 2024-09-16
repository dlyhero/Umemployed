from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users import views
from django.contrib.auth import views as auth_views
from users.views import CustomConfirmEmailView

handler404 = 'users.views.custom_404_view'

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
    
    path('accounts/confirm-email/<str:key>/', CustomConfirmEmailView.as_view(), name='account_confirm_email'),
    
    path('ckeditor/', include('ckeditor_uploader.urls')),
    
    path('resend_confirmation_email/', views.resend_confirmation_email, name='resend_confirmation_email'),
    
    path('error', views.trigger_404, name='test_404'),



    
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
# urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

