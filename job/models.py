from django.db import models
from users.models import User
from company.models import Company
from resume.models import SkillCategory, Skill
import uuid
from resume.models import Resume
from job.utils import calculate_skill_match

class Job(models.Model):
    BEGINNER = 'Beginner'
    MID = 'Mid'
    EXPERT = 'Expert'

    LEVEL_CHOICES = [
        (BEGINNER, 'Beginner'),
        (MID, 'Mid'),
        (EXPERT, 'Expert'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    salary = models.PositiveBigIntegerField(default=35000)
    requirements = models.ManyToManyField(Skill)
    ideal_candidate = models.TextField()
    is_available = models.BooleanField(default=False)
    description = models.TextField(max_length=255, default='We are looking for ...')
    responsibilities = models.TextField(max_length=255, default="You will be in charge of ...")
    benefits = models.TextField(default="...")
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default=BEGINNER)
    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE, default=1)


    def __str__(self):
        return self.title

class MCQ(models.Model):
    question = models.CharField(max_length=255)
    option_a = models.CharField(max_length=100)
    option_b = models.CharField(max_length=100)
    option_c = models.CharField(max_length=100)
    option_d = models.CharField(max_length=100)
    correct_answer = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
    job_title = models.CharField(max_length=100)
class Application(models.Model):
    # id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, default=1)
    quiz_score = models.IntegerField(default=0)
    matching_percentage = models.FloatField(default=0.0)
    overall_match_percentage = models.FloatField(default=0.0)  # New field
    has_completed_quiz = models.BooleanField(default=False)  # New field

    def save(self, *args, **kwargs):
        if self.pk is None:
            from onboarding.models import QuizResponse
            # New application, calculate the quiz score based on the associated job
            quiz_responses = QuizResponse.objects.filter(application=self)
            score = quiz_responses.filter(answer__is_correct=True).count()
            self.quiz_score = score

        applicant_resume = Resume.objects.get(user=self.user)
        applicant_skills = set(applicant_resume.skills.all())
        job_skills = set(self.job.requirements.all())
        match_percentage, missing_skills = calculate_skill_match(applicant_skills, job_skills)

        self.matching_percentage = match_percentage

        overall_match_percentage = (0.7 * match_percentage) + (3 * self.quiz_score)
        self.overall_match_percentage = overall_match_percentage

        super().save(*args, **kwargs)