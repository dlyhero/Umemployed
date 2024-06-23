from django.urls import path
from . import views
from .views import enter_job_description
from .gpt_calls import generate_mcqs, get_skills_from_chatgpt, execute_input
from . import generate_skills
from . import job_description_algorithm

app_name = 'job'


urlpatterns = [
    path('create-job',views.create_job, name="create-job"),
    path('update-job/<int:pk>/',views.update_job, name="update-job"),
    path('apply/<int:job_id>/', views.apply_job, name='apply_job'),
    path('details',views.job_details, name='job_details'),
    path('confirm/<int:job_id>/', views.confirm_evaluation, name='confirm_evaluation'),
    path('enter-job-description/',enter_job_description, name='enter_job_description'),
    path('job/<int:job_id>/save/', views.save_job, name='save_job'),
    path('saved-jobs/', views.view_saved_jobs, name='view_saved_jobs'),
    path('saved-job/<int:saved_job_id>/delete/', views.delete_saved_job, name='delete_saved_job'),
    path('results',views.evaluation_results,name="evaluation_results"),


    #Compiler path
    path('run-code/', views.run_code, name='run_code'),
    path('success/', views.success_page, name='success_page'),
    path('fail/', views.fail_page, name='fail_page'),

    #skills
    path('skills/',views.select_skills,name="select_skills"),

    #quiz
    path('job/<int:job_id>/answer/', views.answer_job_questions, name='answer_job_questions'),
    path('answer/success', views.job_application_success, name='job_application_success'),
    path('get_questions_for_skill/<int:skill_id>/', views.get_questions_for_skill, name='get_questions_for_skill'),
    path('save_responses/', views.save_responses, name='save_responses'),



    path('generate_skills/', get_skills_from_chatgpt, name='generate_skills'),
    path('generate_mcqs/', generate_mcqs, name='generate_mcqs'),
    path('execute_input/', execute_input, name='execute_input'),
    #For generating MCQs per skill when creatung a job, this takes the job_title , the entry level and the skills
    path('generate-questions/', generate_skills.generate_questions_view, name='generate_questions'),
    path('extract-technical-skills/', job_description_algorithm.extract_technical_skills_endpoint, name='extract_technical_skills'),

]
