from django.db import models
from users.models import User
from datetime import date
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
import magic
import uuid
import os

ext_validator = FileExtensionValidator(['pdf', 'docx', 'txt'])  

def validate_file_mime_type(file):
    accept = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain', 'application/zip']
    
    # Read first 1024 bytes to detect MIME type
    file_mime_type = magic.from_buffer(file.read(1024), mime=True)
    print(f'File MIME type: {file_mime_type}')
    
    # Reset file pointer after reading for MIME type detection
    file.seek(0)
    
    # Extract file extension
    ext = os.path.splitext(file.name)[1].lower()
    
    # Allow application/zip for .docx files
    if ext == '.docx' and file_mime_type == 'application/zip':
        file_mime_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    
    # Raise validation error if MIME type is not allowed
    if file_mime_type not in accept:
        raise ValidationError("Unsupported file type")  
    
class SkillCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Skill(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skills', default='1')
    name = models.CharField(max_length=100)
    categories = models.ManyToManyField(SkillCategory)  # Change ForeignKey to ManyToManyField
    is_extracted = models.BooleanField(default=False)  # Indicates whether the skill was extracted from a job description


    def __str__(self):
        return self.name

    

class Education(models.Model):
    resume = models.ForeignKey("Resume", on_delete=models.CASCADE, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    institution_name = models.CharField(max_length=100)
    field_of_study = models.CharField(max_length=255, null=True, blank=True, default='Not specified') 
    degree = models.CharField(max_length=100, default='Not specified')  
    graduation_year = models.IntegerField()

    def __str__(self):
        return self.institution_name


class Experience(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, related_name='experiences')
    resume = models.ForeignKey("Resume", on_delete=models.CASCADE, null=True)
    company_name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.role} at {self.company_name}"


class Resume(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    surname = models.CharField(max_length=100, null=True, blank=True)
    state = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    job_title = models.CharField(max_length=100, null=True, blank=True)
    date_of_birth = models.DateField(default=date.today, null=True)
    phone = models.CharField(max_length=20, null=True)
    description = models.TextField(max_length=500, default="I am a ...")
    profile_image = models.ImageField(upload_to="resume/images", blank=True, default="resume/images/default.jpg")
    cv = models.FileField(upload_to='resume/cv', default="resume/cv/Nyuydine_CV_Resume.pdf", blank=True)
    category = models.ForeignKey(SkillCategory, on_delete=models.CASCADE, null=True)
    skills = models.ManyToManyField(Skill)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        first_name = self.first_name if self.first_name else ""
        surname = self.surname if self.surname else ""
        return first_name + " " + surname

    def calculate_completion_percentage(self):
        required_fields = [
            'first_name', 'surname', 'state', 'country', 'job_title', 
            'date_of_birth', 'phone', 'description', 'profile_image', 'cv'
        ]
        filled_fields = [field for field in required_fields if getattr(self, field)]
        completion_percentage = (len(filled_fields) / len(required_fields)) * 100
        return completion_percentage

    def notify_user_completion(self):
        completion_percentage = self.calculate_completion_percentage()
        if completion_percentage == 100:
            return "Congratulations! Your profile is 100% complete."
        else:
            return f"Your profile is {completion_percentage:.2f}% complete. Please complete the remaining fields."
        
        
class ResumeDoc(models.Model):
    id = models.AutoField(primary_key=True) 
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='resumes/', validators=[ext_validator, validate_file_mime_type])  
    extracted_text = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    extracted_skills = models.ManyToManyField(Skill, blank=True, related_name='resume_extracted_skills')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Resume for {self.user.username}"
    
from django_countries.fields import CountryField
class ContactInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    phone = models.CharField(max_length=20)
    country = CountryField(default='US')  # Default to 'CM' for Cameroon
    # job_title = models.CharField(max_length=100, default='')
    job_title = models.ForeignKey(SkillCategory, on_delete=models.SET_NULL, null=True, blank=True)


    def __str__(self):
        return f"Contact Information for {self.user.username}"
    
class WorkExperience(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, related_name='work_experiences')
    resume = models.ForeignKey("Resume", on_delete=models.CASCADE, null=True)
    company_name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.role} at {self.company_name}"

from django.db import models
from django_countries.fields import CountryField
import pycountry

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    country = CountryField()

    def __str__(self):
        return f"{self.user.username}'s Profile"

class Language(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class UserLanguage(models.Model):
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    language = models.ForeignKey(Language, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user_profile.user.username} - {self.language.name}"