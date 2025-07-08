from django.urls import path

from . import views

urlpatterns = [
    path("general_knowledge_quiz/", views.general_knowledge_quiz, name="general_knowledge_quiz"),
    path("quiz-results/", views.quiz_results, name="quiz_results"),
]
