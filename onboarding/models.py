from django.db import models
from resume.models import Resume
import random

class GeneralKnowledgeQuestion(models.Model):
    question = models.CharField(max_length=200)

    def __str__(self):
        return self.question
class GeneralKnowledgeAnswer(models.Model):
    question = models.ForeignKey(GeneralKnowledgeQuestion, on_delete=models.CASCADE)
    answer = models.CharField(max_length=100)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.answer

from job.models import Application
import uuid
class QuizResponse(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    answer = models.ForeignKey(GeneralKnowledgeAnswer, on_delete=models.CASCADE)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.resume.user.username} - {self.answer.question.question}"

    def save(self, *args, **kwargs):
        if not self.application:
            # If the application is not set, retrieve it based on the associated resume
            self.application = Application.objects.filter(user=self.resume.user, has_completed_quiz=False).first()

        # Save the QuizResponse instance
        super().save(*args, **kwargs)

        # Update the quiz_score for the associated application
        application = self.application
        quiz_responses = QuizResponse.objects.filter(application=application)
        score = quiz_responses.filter(answer__is_correct=True).count()
        application.quiz_score = score
        application.save()