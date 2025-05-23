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
        first_name = self.first_name if self.first_name else "Unknown"
        surname = self.surname if self.surname else "User"
        return f"{first_name} {surname} - {self.job_title if self.job_title else 'No Job Title'}"

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
        
from azure.storage.blob import BlobServiceClient
import os      
account_name = os.getenv('AZURE_ACCOUNT_NAME')
account_key = os.getenv('AZURE_ACCOUNT_KEY')
container_name = os.getenv('AZURE_CONTAINER')
class ResumeDoc(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='resumes/', validators=[ext_validator, validate_file_mime_type])
    extracted_text = models.TextField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    extracted_skills = models.ManyToManyField(Skill, blank=True, related_name='resume_extracted_skills')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Resume for {self.user.username}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Upload the file to Azure Blob Storage
        account_name = os.getenv('AZURE_ACCOUNT_NAME')
        account_key = os.getenv('AZURE_ACCOUNT_KEY')
        container_name = os.getenv('AZURE_CONTAINER')

        connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=self.file.name)

        try:
            with open(self.file.path, 'rb') as data:
                blob_client.upload_blob(data, overwrite=True)
            print(f"File uploaded to Azure Blob Storage: {self.file.name}")
        except Exception as e:
            print(f"Error uploading file to Azure Blob Storage: {e}")

    def __str__(self):
        return f"Resume for {self.user.username}"
    
from django_countries.fields import CountryField
class ContactInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    phone = models.CharField(max_length=20)
    country = CountryField(default='US')  # Default to 'US'
    job_title = models.ForeignKey(SkillCategory, on_delete=models.SET_NULL, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)  # New field
    city = models.CharField(max_length=100, null=True, blank=True)  # New field

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Update corresponding fields in the existing Resume model
        resume = Resume.objects.filter(user=self.user).first()
        if not resume:
            resume = Resume(user=self.user)
        name_parts = self.name.split(" ", 1)
        resume.first_name = name_parts[0] if len(name_parts) > 0 else ""
        resume.surname = name_parts[1] if len(name_parts) > 1 else ""
        resume.phone = self.phone
        resume.country = self.country.name
        resume.state = self.city  # Map city to state in Resume
        resume.date_of_birth = self.date_of_birth  # Map date_of_birth
        resume.job_title = self.job_title.name if self.job_title else None
        resume.save()

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
    resume_analysis_attempts = models.PositiveIntegerField(default=0)


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
    
class ResumeAnalysis(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='resume_analyses')
    resume = models.ForeignKey(ResumeDoc, on_delete=models.CASCADE, related_name='analyses')
    overall_score = models.FloatField()
    criteria_scores = models.JSONField()  # Stores scores for each criterion
    improvement_suggestions = models.JSONField()  # Stores improvement suggestions
    analyzed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Resume Analysis for {self.user.username} on {self.analyzed_at}"
    
class Transcript(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='transcripts/')
    extracted_text = models.TextField(blank=True, null=True)
    job_title = models.CharField(max_length=255, blank=True, null=True)  # New field
    reasoning = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transcript for {self.user.username}"

class ProfileView(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

class EnhancedResume(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job = models.ForeignKey('job.Job', on_delete=models.CASCADE)
    full_name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    skills = models.JSONField(blank=True, null=True)  # List of skills
    experience = models.JSONField(blank=True, null=True)  # List of jobs
    education = models.JSONField(blank=True, null=True)  # List of education entries
    certifications = models.JSONField(blank=True, null=True)
    projects = models.JSONField(blank=True, null=True)
    languages = models.JSONField(blank=True, null=True)
    awards = models.JSONField(blank=True, null=True)
    publications = models.JSONField(blank=True, null=True)
    volunteer_experience = models.JSONField(blank=True, null=True)
    interests = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Enhanced Resume for {self.user.username} - Job {self.job.id}"

