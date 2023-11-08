from django.db import models
from users.models import User
from datetime import date
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
import magic

ext_validator = FileExtensionValidator(['pdf',])

def validate_file_mime_type(file):
    accept = ['application/pdf']
    file_mime_type = magic.from_buffer(file.read(1024), mime=True)
    print('file_mime_type')
    if file_mime_type not in accept:
        raise ValidationError("Unsupported file type")

class SkillCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Skill(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Resume(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    surname = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    job_title = models.CharField(max_length=100, null=True, blank=True)
    date_of_birth = models.DateField(default=date.today().strftime("%Y-%m-%d"))
    phone = models.CharField(max_length=20, null=True)
    description= models.TextField(max_length=500, default="I am a ...")
    profile_image = models.ImageField(upload_to="resume/images", blank=True, default="")
    cv = models.FileField(upload_to='resume/cv', default="", blank=False, validators=[ext_validator, validate_file_mime_type])
    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE, default='1')
    skills = models.ManyToManyField(Skill)
    experience = models.CharField(max_length=250, default='None')
    education = models.CharField(max_length=50,default='None')



    def __str__(self):
        first_name = self.first_name if self.first_name else ""
        surname = self.surname if self.surname else ""
        return first_name + " " + surname