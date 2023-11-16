from django.db import models
from users.models import User
from company.models import Company
from resume.models import SkillCategory, Skill


class Job(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    salary = models.PositiveBigIntegerField(default=35000)
    requirements = models.ManyToManyField(Skill)
    ideal_candidate = models.TextField()
    is_available = models.BooleanField(default=False)

    def __str__(self):
        return self.title
    