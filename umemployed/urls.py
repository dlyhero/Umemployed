from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('users.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('',views.home, name = 'home'),
    path('accounts/google/', include('allauth.urls')),

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
    path('jobs/',include('website.urls'))
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)