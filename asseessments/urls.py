from . import views
from django.urls import path



urlpatterns = [
    path('',views.assessments, name='assessments'),
    path('detail',views.assessment_detail, name='assessment_detail'),

 # URLs for CRUD operations of assessment models
    path('assessment/create/', views.create_assessment, name='create_assessment'),
    path('assessment/update/<int:assessment_id>/', views.update_assessment, name='update_assessment'),
    path('assessment/delete/<int:assessment_id>/', views.delete_assessment, name='delete_assessment'),
    path('assessment/list/', views.assessment_list, name='assessment_list'),
    path('assessment/detail/<int:assessment_id>/', views.assessment_detail, name='assessment_detail'),
    # URLs for user views
    path('user/assessments/', views.available_assessments, name='available_assessments'),
    path('user/session/start/<int:assessment_id>/', views.start_session, name='start_session'),
    path('user/session/submit/<int:session_id>/', views.submit_session, name='submit_session'),
    path('session-details/<int:session_id>/', views.session_details, name='session_details'),
    path('user/session/results/<int:session_id>/', views.session_results, name='session_results'),
]