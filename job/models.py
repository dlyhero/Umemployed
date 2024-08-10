from django.db import models
from users.models import User
from company.models import Company
from resume.models import SkillCategory, Skill
import uuid
from resume.models import Resume
from job.utils import calculate_skill_match
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

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
    hire_number = models.IntegerField()
    job_location_type = models.CharField(max_length=50, choices=[
        ('remote', 'Remote'),
        ('onsite', 'Onsite'),
        ('hybrid', 'Hybrid'),
        ('internship', 'Internship'),
    ])
    location = models.CharField(max_length=100)
    salary = models.PositiveBigIntegerField(default=35000)
    requirements = models.ManyToManyField(Skill, related_name='required_jobs')
    extracted_skills = models.ManyToManyField(Skill, blank=True, related_name='extracted_jobs')
    ideal_candidate = models.TextField()
    is_available = models.BooleanField(default=False)
    description = models.TextField(max_length=255, default='We are looking for ...')
    responsibilities = models.TextField(max_length=255, default="You will be in charge of ...")
    benefits = models.TextField(default="...")
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default=BEGINNER)
    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE, default=1)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job_type = models.CharField(max_length=255, blank=True)
    experience_levels = models.CharField(max_length=255, blank=True)
    weekly_ranges = models.CharField(max_length=255, blank=True)
    shifts = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Add this line
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.title

class MCQ(models.Model):
    id = models.BigAutoField(primary_key=True)
    question = models.CharField(max_length=255)
    option_a = models.CharField(max_length=100)
    option_b = models.CharField(max_length=100)
    option_c = models.CharField(max_length=100)
    option_d = models.CharField(max_length=100)
    correct_answer = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
    job_title = models.ForeignKey(SkillCategory, on_delete=models.CASCADE, related_name='mcq_questions')

    def __str__(self):
        return self.question
    
class SkillQuestion(models.Model):
    id = models.BigAutoField(primary_key=True)
    question = models.CharField(max_length=255)
    option_a = models.CharField(max_length=100)
    option_b = models.CharField(max_length=100)
    option_c = models.CharField(max_length=100)
    option_d = models.CharField(max_length=100)
    correct_answer = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    entry_level = models.CharField(max_length=100, blank=True, null=True)  # Assuming entry level is a string field
    job = models.ForeignKey(Job, on_delete=models.CASCADE,null=True, related_name='skill_questions')

    def __str__(self):
        return self.question

class ApplicantAnswer(models.Model):
    id = models.BigAutoField(primary_key=True)
    applicant = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    question = models.ForeignKey('SkillQuestion', on_delete=models.CASCADE)
    answer = models.CharField(max_length=255)
    job = models.ForeignKey('Job', on_delete=models.CASCADE)
    score = models.IntegerField(default=0)
    application = models.ForeignKey('Application', on_delete=models.CASCADE, related_name='answers')

    def calculate_score(self):
        if hasattr(self.question, 'correct_answer') and self.answer == self.question.correct_answer:
            self.score = 1
        else:
            self.score = 0
        self.save()


        
logger = logging.getLogger(__name__)

class Application(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job = models.ForeignKey('Job', on_delete=models.CASCADE)
    quiz_score = models.IntegerField(default=0)
    matching_percentage = models.FloatField(default=0.0)
    overall_match_percentage = models.FloatField(default=0.0)
    has_completed_quiz = models.BooleanField(default=False)
    round_scores = models.JSONField(default=dict)
    total_scores = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        logger.debug(f"Calling save method for Application")
        self.update_quiz_score()
        self.update_matching_percentage()
        self.update_total_scores()
        
        self.has_completed_quiz = self.is_quiz_completed()
        
        logger.debug(f"Application saved with quiz_score: {self.quiz_score}, has_completed_quiz: {self.has_completed_quiz}")
        super().save(*args, **kwargs)

    def is_quiz_completed(self):
        required_skills = set(self.job.requirements.values_list('id', flat=True))
        completed_skills = set(int(skill_id) for skill_id in self.round_scores.keys())
        logger.debug(f"Checking if quiz is completed")
        return required_skills <= completed_skills

    def update_quiz_score(self):
        total_correct_answers = ApplicantAnswer.objects.filter(application=self, score=1).count()
        self.quiz_score = total_correct_answers
        logger.debug(f"Updated quiz score: {self.quiz_score}")

    def update_matching_percentage(self):
        try:
            applicant_resume = Resume.objects.get(user=self.user)
            applicant_skills = set(applicant_resume.skills.all())
            job_skills = set(self.job.requirements.all())
            match_percentage, _ = calculate_skill_match(applicant_skills, job_skills)

            self.matching_percentage = match_percentage
            self.overall_match_percentage = (0.7 * match_percentage) + (0.3 * self.quiz_score)
            logger.debug(f"Updated matching percentage: {self.matching_percentage}, overall match percentage: {self.overall_match_percentage}")
        except Resume.DoesNotExist:
            self.matching_percentage = 0.0
            self.overall_match_percentage = 0.0

    def update_total_scores(self):
        self.total_scores = {}
        for skill_id in self.round_scores:
            answers = ApplicantAnswer.objects.filter(applicant=self.user, job=self.job, question__skill_id=skill_id)
            total_score = sum(answer.score for answer in answers)
            self.total_scores[skill_id] = total_score
        logger.debug(f"Updated total scores: {self.total_scores}")

    @staticmethod
    def calculate_skill_match(applicant_skills, job_skills):
        if not job_skills:
            return 0, []
        common_skills = set(applicant_skills) & set(job_skills)
        match_percentage = (len(common_skills) / len(job_skills)) * 100
        missing_skills = list(set(job_skills) - common_skills)
        return match_percentage, missing_skills
            
            
from django.utils import timezone
class CompletedSkills(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, null=True)
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, null=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ['user', 'job', 'skill']
        
class SavedJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')