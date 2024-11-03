from django.db import models
from users.models import User
from company.models import Company
from resume.models import SkillCategory, Skill
import uuid
from resume.models import Resume
from job.utils import calculate_skill_match
from django.conf import settings
from ckeditor.fields import RichTextField
from django.urls import reverse
from django_countries.fields import CountryField
from decimal import Decimal



import logging

logger = logging.getLogger(__name__)

class Job(models.Model):
    """
    Represents a job listing created by a user for a specific company.
    """
    BEGINNER = 'Beginner'
    MID = 'Mid'
    EXPERT = 'Expert'

    LEVEL_CHOICES = [
        (BEGINNER, 'Beginner'),
        (MID, 'Mid'),
        (EXPERT, 'Expert'),
    ]

    FULL_TIME = 'Full_time'
    PART_TIME = 'Part_time'
    CONTRACT = 'Contract'
    TEMPORARY = 'Temporary'
    INTERNSHIP = 'Internship'
    FREELANCE = 'Freelance'

    JOB_TYPE_CHOICES = [
        (FULL_TIME, 'Full-Time'),
        (PART_TIME, 'Part-Time'),
        (CONTRACT, 'Contract'),
        (TEMPORARY, 'Temporary'),
        (INTERNSHIP, 'Internship'),
        (FREELANCE, 'Freelance'),
    ]

    EXPERIENCE_LEVEL_CHOICES = [
        ('noExperience', 'No Experience Needed'),
        ('under1Year', 'Under 1 Year'),
        ('1-3Years', '1-3 Years'),
        ('3-5Years', '3-5 Years'),
        ('5-10Years', '5-10 Years'),
        ('10+Years', '10+ Years'),
    ]

    WEEKLY_RANGE_CHOICES = [
        ('mondayToFriday', 'Monday to Friday'),
        ('weekendsNeeded', 'Weekends Needed'),
        ('everyWeekend', 'Every Weekend'),
        ('rotatingWeekend', 'Rotating Weekend'),
        ('noneWeekend', 'None Weekend'),
        ('weekendsOnly', 'Weekends Only'),
        ('other', 'Other'),
    ]

    SHIFT_CHOICES = [
        ('morningShift', 'Morning Shift'),
        ('dayShift', 'Day Shift'),
        ('eveningShift', 'Evening Shift'),
        ('nightShift', 'Night Shift'),
        ('eightHourShift', '8 Hours Shift'),
        ('tenHourShift', '10 Hours Shift'),
        ('twelveHourShift', '12 Hours Shift'),
        ('otherShift', 'Other'),
        ('noneShift', 'None'),
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
    location = CountryField(blank_label='(Select Country)', null=True)
    salary = models.PositiveBigIntegerField(default=35000)
    salary_range = models.CharField(max_length=20, choices=[
        ('30000-50000', '$30,000 - $50,000'),
        ('50001-70000', '$50,001 - $70,000'),
        ('70001-100000', '$70,001 - $100,000'),
        ('100001-150000', '$100,001 - $150,000'),
        ('150001+', '$150,001 and above'),
    ], default='30000-50000')
    requirements = models.ManyToManyField(Skill, related_name='required_jobs')
    extracted_skills = models.ManyToManyField(Skill, blank=True, related_name='extracted_jobs')
    ideal_candidate = RichTextField()
    is_available = models.BooleanField(default=False)
    description = RichTextField(max_length=2000, default='We are looking for ...')
    responsibilities = RichTextField(max_length=1000, default="You will be in charge of ...")
    benefits = RichTextField(default="...")
    level = models.CharField(max_length=10, choices=LEVEL_CHOICES, default=BEGINNER)
    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE, default=1)
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, blank=True, verbose_name='Job Type')
    experience_levels = models.CharField(max_length=255, choices=EXPERIENCE_LEVEL_CHOICES, blank=True)
    weekly_ranges = models.CharField(max_length=255, choices=WEEKLY_RANGE_CHOICES, blank=True)
    shifts = models.CharField(max_length=255, choices=SHIFT_CHOICES, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return reverse('job:job_details', args=[str(self.id)])
    
    def __str__(self):
        return self.title

class MCQ(models.Model):
    """Model for Multiple Choice Questions."""
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
    """Model for Skill Questions."""
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
    area = models.CharField(max_length=255, blank=True, null=True)  # New field for area of expertise

    def __str__(self):
        return self.question

class ApplicantAnswer(models.Model):
    """Model for Applicant's answers."""
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
    """Model for Application."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('rejected', 'Rejected'),
        ('accepted', 'Accepted'),
    ]

    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    job = models.ForeignKey('Job', on_delete=models.CASCADE)
    quiz_score = models.IntegerField(default=0)
    matching_percentage = models.FloatField(default=0.0)
    overall_match_percentage = models.DecimalField(
        max_digits=5,  # Total number of digits
        decimal_places=2,  # Number of decimal places
        default=Decimal('0.00')
    )    
    has_completed_quiz = models.BooleanField(default=False)
    round_scores = models.JSONField(default=dict)
    total_scores = models.JSONField(default=dict)
    video_file = models.FileField(upload_to='videos/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        logger.debug("Calling save method for Application")
        self.update_quiz_score()
        self.update_matching_percentage()
        self.update_total_scores()
        
        self.has_completed_quiz = self.is_quiz_completed()
        
        # Check and create CompletedSkills if the quiz is completed
        if self.has_completed_quiz:
            self.create_completed_skills()

        # Determine status based on conditions
        if self.overall_match_percentage >= 80:
            self.status = 'accepted'
        elif self.overall_match_percentage < 50:
            self.status = 'rejected'
        else:
            self.status = 'pending'

        logger.debug(f"Application saved with quiz_score: {self.quiz_score}, has_completed_quiz: {self.has_completed_quiz}, status: {self.status}")
        super().save(*args, **kwargs)

    def is_quiz_completed(self):
        required_skills = set(self.job.requirements.values_list('id', flat=True))
        completed_skills = set(int(skill_id) for skill_id in self.round_scores.keys())
        logger.debug("Checking if quiz is completed")
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

            match_percentage, _ = self.calculate_skill_match(applicant_skills, job_skills)

            total_questions = SkillQuestion.objects.filter(skill__in=job_skills, entry_level=self.job.level).count()
            user_total_score = ApplicantAnswer.objects.filter(
                applicant=self.user, job=self.job, question__skill__in=job_skills
            ).aggregate(total_score=models.Sum('score'))['total_score'] or 0

            skill_based_score = (user_total_score / total_questions) * 100 if total_questions > 0 else 0

            self.matching_percentage = match_percentage
            self.overall_match_percentage =  skill_based_score

            logger.debug(f"Updated matching percentage: {self.matching_percentage}, overall match percentage: {self.overall_match_percentage}")
        except Resume.DoesNotExist:
            self.matching_percentage = 0.0
            self.overall_match_percentage = 0.0
            logger.error(f"No resume found for user {self.user}")
        except Exception as e:
            logger.error(f"Error updating matching percentage: {e}")

    def update_total_scores(self):
        self.total_scores = {}
        for skill_id in self.round_scores:
            answers = ApplicantAnswer.objects.filter(applicant=self.user, job=self.job, question__skill_id=skill_id)
            total_score = sum(answer.score for answer in answers)
            self.total_scores[skill_id] = total_score
        logger.debug(f"Updated total scores: {self.total_scores}")

    def create_completed_skills(self):
        completed_skills = self.round_scores.keys()
        logger.debug(f"Attempting to create or update completed skills for skills: {completed_skills}")

        for skill_id in completed_skills:
            try:
                # Retrieve the Skill instance
                skill = Skill.objects.get(id=skill_id)
                logger.debug(f"Retrieved Skill with ID: {skill_id}")

                # Create or update CompletedSkills
                completed_skill, created = CompletedSkills.objects.get_or_create(
                    user=self.user,
                    job=self.job,
                    skill=skill,
                    defaults={'is_completed': True}
                )

                if created:
                    logger.debug(f"Created new CompletedSkills for skill_id: {skill_id}")
                else:
                    completed_skill.is_completed = True
                    completed_skill.completed_at = timezone.now()
                    completed_skill.save()
                    logger.debug(f"Updated CompletedSkills for skill_id: {skill_id}")

            except Skill.DoesNotExist:
                logger.error(f"Skill with ID {skill_id} does not exist.")
            except Exception as e:
                logger.error(f"Error processing skill_id {skill_id}: {str(e)}")


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