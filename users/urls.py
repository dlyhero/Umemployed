from django.urls import path,include
from . import views
import resume.urls 
from django.views.generic import TemplateView

urlpatterns = [
    path('register-applicant', views.register_applicant,name='register-applicant'),
    path('register-recruiter', views.register_recruiter,name='register-recruiter'),
    path('login', views.login_user,name='login'),
    path('logout/', views.logout_user,name='logout'),
    path('role/',views.switch_account,name='switch_account'),
    path('upload/',include(resume.urls)),
    path('switch-type',views.change_account_type,name="change_account_type"),
    path('switch-account-type',views.switch_account_type,name="switch_account_type"),
    
    
    path('verify',views.send_verification_to_unverified_users, name='send_verification_to_unverified_users'),
    path('account/email-verification-sent/', TemplateView.as_view(template_name='account/verification_sent.html'), name='account_email_verification_sent'),

    

]
