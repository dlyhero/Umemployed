from django.urls import path,include
from . import views
import resume.urls 

urlpatterns = [
    path('register-applicant', views.register_applicant,name='register-applicant'),
    path('register-recruiter', views.register_recruiter,name='register-recruiter'),
    path('login', views.login_user,name='login'),
    path('logout/', views.logout_user,name='logout'),
    path('role/',views.switch_account,name='switch_account'),
    path('upload/',include(resume.urls)),
    path('switch-type',views.change_account_type,name="change_account_type"),
    path('switch-account-type',views.switch_account_type,name="switch_account_type"),

    

]
