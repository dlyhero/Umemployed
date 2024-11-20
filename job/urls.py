from django.urls import path,include
from . import views
from .views import enter_job_description
from .gpt_calls import generate_mcqs, get_skills_from_chatgpt, execute_input
from . import generate_skills
from . import job_description_algorithm

app_name = 'job'


urlpatterns = [
    path('create-job',views.create_job, name="create-job"),
    path('job_type_view/',views.job_type_view, name="job_type_view"),
    path('update-job/<int:pk>/',views.update_job, name="update-job"),
    path('apply/<int:job_id>/', views.apply_job, name='apply_job'),
    path('details/<int:job_id>/',views.job_details, name='job_details'),
    path('job-details/<int:job_id>/',views.job_listing_details, name='job_listing_details'),
    path('confirm/<int:job_id>/', views.confirm_evaluation, name='confirm_evaluation'),
    path('enter-job-description/',enter_job_description, name='enter_job_description'),
    path('job/<int:job_id>/save/', views.save_job, name='save_job'),
    path('save-job/<int:job_id>/', views.save_job_not_ajax, name='save_job_not_ajax'),  # Add this line
    path('saved-jobs/', views.saved_jobs_view, name='view_saved_jobs'),
    path('saved-job/<int:saved_job_id>/delete/', views.delete_saved_job, name='delete_saved_job'),
    path('results/<int:job_id>/',views.evaluation_results,name="evaluation_results"),
    path('update/<int:job_id>/', views.update_job, name='update_job'),
    
    path('incomplete-jobs/', views.incomplete_jobs_view, name='incomplete_jobs'),

    
    path('save_video/', views.save_video, name='save_video'),


    


    #Compiler path
    path('run-code/', views.run_code, name='run_code'),
    path('success/', views.success_page, name='success_page'),
    path('fail/', views.fail_page, name='fail_page'),

    #skills
    path('select-skills/',views.select_skills,name="select_skills"),

    #quiz
    path('job/<int:job_id>/answer/', views.answer_job_questions, name='answer_job_questions'),
    path('answer/<int:job_id>/success', views.job_application_success, name='job_application_success'),
    path('get_questions_for_skill/<int:skill_id>/', views.get_questions_for_skill, name='get_questions_for_skill'),
    path('save_responses/', views.save_responses, name='save_responses'),



    path('generate_skills/', get_skills_from_chatgpt, name='generate_skills'),
    path('generate_mcqs/', generate_mcqs, name='generate_mcqs'),
    path('execute_input/', execute_input, name='execute_input'),
    #For generating MCQs per skill when creatung a job, this takes the job_title , the entry level and the skills
    path('generate-questions/', generate_skills.generate_questions_view, name='generate_questions'),
    path('extract-technical-skills/', job_description_algorithm.extract_technical_skills_endpoint, name='extract_technical_skills'),

    path('applied-jobs/', views.user_applied_jobs, name='applied_jobs'),
    path('withdraw-application/<int:job_id>/', views.withdraw_application, name='withdraw_application'),
    path('save-job/<int:job_id>/', views.save_job, name='save_job'),
    path('remove-saved-job/<int:job_id>/', views.remove_saved_job, name='remove_saved_job'),
    path('saved-jobs/', views.saved_jobs_view, name='saved_jobs'),
    
    path('jobs/<int:job_id>/shortlist/<int:candidate_id>/', views.shortlist_candidate, name='shortlist_candidate'),
    path('jobs/shortlisted/<int:company_id>/', views.shortlisted_candidates, name='shortlisted'),
    path('jobs/<int:job_id>/decline/<int:candidate_id>/', views.decline_candidate, name='decline_candidate'),
    
    path('issue/<int:job_id>/', views.report_test, name='report_test'),

 
    

]
