from django.db import models
from resume.models import Resume
import random

class GeneralKnowledgeQuestion(models.Model):
    """
    Model to store general knowledge questions.

    Attributes:
        question (str): The text of the question.
    """
    question = models.CharField(max_length=200)

    def __str__(self):
        """
        String representation of the question.

        Returns:
            str: The text of the question.
        """
        return self.question

class GeneralKnowledgeAnswer(models.Model):
    """
    Model to store general knowledge answers.

    Attributes:
        question (ForeignKey): The question to which this answer belongs.
        answer (str): The text of the answer.
        is_correct (bool): Indicates if this answer is correct or not.
    """
    question = models.ForeignKey(GeneralKnowledgeQuestion, on_delete=models.CASCADE)
    answer = models.CharField(max_length=100)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        """
        String representation of the answer.

        Returns:
            str: The text of the answer.
        """
        return self.answer

from job.models import Application
import uuid

class QuizResponse(models.Model):
    """
    Model to store quiz responses.

    Attributes:
        resume (ForeignKey): The resume associated with this response.
        answer (ForeignKey): The selected answer.
        application (ForeignKey): The application associated with this response.
        created_at (DateTimeField): The date and time when the response was created.
    """
    resume = models.ForeignKey(Resume, on_delete=models.CASCADE)
    answer = models.ForeignKey(GeneralKnowledgeAnswer, on_delete=models.CASCADE)
    application = models.ForeignKey(Application, on_delete=models.CASCADE, default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        String representation of the quiz response.

        Returns:
            str: The username of the resume owner and the associated question.
        """
        return f"{self.resume.user.username} - {self.answer.question.question}"

    def save(self, *args, **kwargs):
        """
        Custom save method to update application quiz score after saving the response.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
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
