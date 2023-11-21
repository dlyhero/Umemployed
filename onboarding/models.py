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

class QuizResponse(models.Model):
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    answer = models.ForeignKey(GeneralKnowledgeAnswer, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.resume.user.username} - {self.answer.question.question}"
