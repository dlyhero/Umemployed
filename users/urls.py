from django.urls import path, include
from . import views
import resume.urls
from django.views.generic import TemplateView

urlpatterns = [
    path('register-applicant/', views.register_applicant, name='register-applicant'),
    path('register-recruiter/', views.register_recruiter, name='register-recruiter'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('role/', views.switch_account, name='switch_account'),
    path('upload/', include(resume.urls)),
    path('switch-type/', views.change_account_type, name="change_account_type"),
    path('switch-account-type/', views.switch_account_type, name="switch_account_type"),
    path('verify/', views.send_verification_to_unverified_users, name='send_verification_to_unverified_users'),
    path('account/email-verification-sent/', TemplateView.as_view(template_name='account/verification_sent.html'), name='account_email_verification_sent'),
    path('user_dashboard/', views.user_dashboard, name='dashboard'),
    path('career-resources/', views.career_resources, name='career_resources'),
    path('feature-not-implemented/', views.feature_not_implemented, name='feature-not-implemented'),
    path('resume/<int:user_id>/', views.user_resume, name='user_resume'),
    path('set-password/', views.set_password, name='set_password'),
    path('about/', views.about_us, name='about_us'),
    path('accessibility/', views.accessibility, name='accessibility'),
    path('employers/', views.for_employers, name='for_employers'),
    path('policies/', views.community_guidelines, name='community_guidelines'),
    path('careers/', views.work_with_us, name='work_with_us'),
    path('advertise/', views.advertise_jobs, name='advertise_jobs'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('terms/', views.terms_of_service, name='terms_of_service'),
    path('safety/', views.safety_center, name='safety_center'),
    path('blog/', views.blog, name='blog'),
    path('contact/', views.contact_us, name='contact_us'),
    path('partners/', views.partners, name='partners'),
]
