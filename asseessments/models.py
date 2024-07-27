# models.py
from django.db import models
from users.models import User

class Assessment(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    duration = models.PositiveIntegerField()
    # Other fields as per your requirements

class Question(models.Model):
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    question_text = models.TextField()

class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    option_text = models.CharField(max_length=255)
    is_correct = models.BooleanField(default=False)

class Session(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)

class Result(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    selected_option = models.ForeignKey(Option, on_delete=models.CASCADE)
    # Any other fields you might need for result tracking