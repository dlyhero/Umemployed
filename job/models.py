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
    requirements = models.ManyToManyField(Skill, related_name='required_jobs')
    extracted_skills = models.ManyToManyField(Skill, blank=True, related_name='extracted_jobs')
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.CharField(max_length=255)
    option_a = models.CharField(max_length=100)
    option_b = models.CharField(max_length=100)
    option_c = models.CharField(max_length=100)
    option_d = models.CharField(max_length=100)
    correct_answer = models.CharField(max_length=1, choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')])
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE)
    entry_level = models.CharField(max_length=100, blank=True, null=True)  # Assuming entry level is a string field

    def __str__(self):
        return self.question

class ApplicantAnswer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    applicant = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey('SkillQuestion', on_delete=models.CASCADE)  # Update this line
    answer = models.CharField(max_length=255)
    job = models.ForeignKey('Job', on_delete=models.CASCADE)
    score = models.IntegerField(default=0)  # Add score field

    def __str__(self):
        return f"Answer by {self.applicant.username} for {self.question.question}"

    def calculate_score(self):
        if self.answer == self.question.correct_answer:
            self.score = 1
        else:
            self.score = 0
        self.save()
class Application(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, default=1)
    quiz_score = models.IntegerField(default=0)
    matching_percentage = models.FloatField(default=0.0)
    overall_match_percentage = models.FloatField(default=0.0)
    has_completed_quiz = models.BooleanField(default=False)
    # Assume you may have many rounds based on the number of skills
    round_scores = models.JSONField(default=dict)  # Store scores for each skill/round as a dictionary
    total_scores = models.JSONField(default=dict)  # Store total score for each skill/round as a dictionary


    def save(self, *args, **kwargs):
        if self.pk is None:
            from onboarding.models import QuizResponse

            # Initial calculation for quiz_score
            quiz_responses = QuizResponse.objects.filter(application=self)
            self.quiz_score = quiz_responses.filter(answer__is_correct=True).count()

            applicant_answers = ApplicantAnswer.objects.filter(applicant=self.user, job=self.job)
            quiz_score_from_answers = applicant_answers.filter(score=1).count()
            self.quiz_score += quiz_score_from_answers

            applicant_resume = Resume.objects.get(user=self.user)
            applicant_skills = set(applicant_resume.skills.all())
            job_skills = set(self.job.requirements.all())
            match_percentage, _ = calculate_skill_match(applicant_skills, job_skills)

            self.matching_percentage = match_percentage
            self.overall_match_percentage = (0.7 * match_percentage) + (30 * self.quiz_score)

        # Calculate and update total_scores for each skill/round
        self.update_total_scores()

        super().save(*args, **kwargs)  # Save the instance without recursion

    def update_total_scores(self):
        for skill_id in self.round_scores:
            answers = ApplicantAnswer.objects.filter(applicant=self.user, job=self.job, question__skill_id=skill_id)
            total_score = sum(answer.score for answer in answers)
            self.total_scores[skill_id] = total_score

class CompletedSkills(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job_id = models.IntegerField()  # Example: Assuming job_id is an integer
    skill_id = models.IntegerField()  # Example: Assuming skill_id is an integer
    is_completed = models.BooleanField(default=False)  # New field to track completion status

    class Meta:
        unique_together = ['user', 'job_id', 'skill_id']

    def __str__(self):
        return f"CompletedSkills(user={self.user}, job_id={self.job_id}, skill_id={self.skill_id}, is_completed={self.is_completed})"
        
        
class SavedJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'job')