from . import views
from django.urls import path

urlpatterns = [
    path('',views.assessments, name='assessments'),
    path('detail',views.assessment_detail, name='assessment_detail'),

]
