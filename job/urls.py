from django.urls import path
from . import views
app_name = 'job'


urlpatterns = [
    path('create-job',views.create_job, name="create-job"),
    path('update-job/<int:pk>/',views.update_job, name="update-job"),
    path('apply/<int:job_id>/', views.apply_job, name='apply_job'),
    path('details',views.job_details, name='job_details'),
    path('confirm/<int:job_id>/', views.confirm_evaluation, name='confirm_evaluation'),


    #Compiler path
    path('run-code/', views.run_code, name='run_code'),
    path('success/', views.success_page, name='success_page'),
    path('fail/', views.fail_page, name='fail_page'),

    #skills
    path('skills/',views.select_skills,name="select_skills"),

    #quiz
    path('job/<int:job_id>/answer/', views.answer_job_questions, name='answer_job_questions'),
    path('answer/success', views.job_application_success, name='job_application_success'),


]
