from pypdf import PdfReader 
from django.http import HttpResponse
from django.shortcuts import render,redirect,get_object_or_404
import json
import logging
from openai import OpenAI
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from job.models import Skill, SkillQuestion
import os
from resume.models import SkillCategory,Skill
import dotenv

dotenv.load_dotenv()
api_key = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)
logger = logging.getLogger(__name__)

import json
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


api_key = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)
from .forms import ResumeForm

from django.urls import reverse
from django.shortcuts import redirect

def save_skills_to_database(job_title, skills):
    try:
        # Retrieve or create the SkillCategory object based on the job_title
        category, created = SkillCategory.objects.get_or_create(name=job_title)

        # Create Skill objects and associate them with the SkillCategory
        for skill_name in skills:
            skill, created = Skill.objects.get_or_create(name=skill_name)
            skill.categories.add(category)  # Associate the skill with the category
            skill.is_extracted = True  # Set the flag indicating that this skill was extracted from a job description
            skill.save()

    except Exception as e:
        logger.error("An error occurred while saving skills to the database for %s: %s", job_title, e)




def upload_resume(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            resume = form.save(commit=False)
            resume.user = request.user
            resume.save()
            # Generate the URL for the extract_text view with the file_path parameter
            file_path = resume.file.url.lstrip('/')
            redirect_url = reverse('extract_text', kwargs={'file_path': file_path})
            # Redirect to the extract_text view
            return redirect(redirect_url)
    else:
        form = ResumeForm()
    return render(request, 'resume/upload_resume.html', {'form': form})



from .models import *

from django.http import HttpResponse
from job.models import Job


def extract_text(request, file_path):
    # Creating a pdf reader object 
    reader = PdfReader(file_path) 

    # Creating a page object 
    page = reader.pages[0] 
    extracted_text = page.extract_text()

    # Get the job title from Resume.job_title based on extracted text
    try:
        resume = Resume.objects.get(user = request.user)
        job_title = resume.job_title
        print("Job title found:", job_title)
    except Resume.DoesNotExist:
        print("Resume not found for extracted text:", extracted_text)
        # Handle the case where the Resume object does not exist
        # You may want to return an error response or redirect to an error page
        return HttpResponse("Error: Resume not found")

    # Save the extracted text to the database
    try:
        print("Searching for ResumeDoc with file path:", file_path)
        resume_doc = ResumeDoc.objects.get(file=file_path)
        print("ResumeDoc found:", resume_doc)
        resume_doc.extracted_text = extracted_text
        resume_doc.save()
        print("Extracted text saved to ResumeDoc")
    except ResumeDoc.DoesNotExist:
        print("ResumeDoc not found for file path:", file_path)
        # Handle the case where the ResumeDoc object does not exist
        # You may want to return an error response or redirect to an error page
        pass

    # Redirect to the extract_technical_skills view
    technical_skills = extract_technical_skills(request, extracted_text, job_title)
    return HttpResponse("Text extraction successful")




def extract_technical_skills(request, extracted_text, job_title):
    conversation = [
        {
            "role": "user", 
            "content": f"Given the following resume details: {extracted_text}, identify and list all the technical skills that can be practically tested during a technical interview. Focus on extracting skills related to hands-on technical knowledge, coding abilities, use of specific software tools, problem-solving skills, and any other competencies that can be demonstrated through practical tests, coding challenges, or problem-solving exercises. Exclude skills that cannot be directly tested in an interview setting, such as soft skills or theoretical knowledge not applicable to practical tasks. Format your output in JSON, organizing the skills under a key named 'Technical Skills'. Each skill should be listed as an element in an array of strings. Ensure that each skill does not comprise more than two words."
        }
    ]

    try:
        # Call GPT-4 to generate technical skills based on resume data
        response = client.chat.completions.create(
            model="gpt-4",
            messages=conversation
        )

        # Parse the response
        response_content = response.choices[0].message.content
        response_dict = json.loads(response_content)
        

        # Extract the technical skills
        technical_skills = response_dict.get("Technical Skills", [])
        print(technical_skills)
        for skill in technical_skills:
            skill_obj, created = Skill.objects.get_or_create(name=skill)
            # Access the extracted_skills attribute of the ResumeDoc instance associated with the current user
            resume_doc = ResumeDoc.objects.get(user=request.user)  # Assuming there's only one ResumeDoc per user
            resume_doc.extracted_skills.add(skill_obj)
        # Save the skills to the database
        save_skills_to_database(job_title, technical_skills)
        print('Skills saved to database:', technical_skills)

        return technical_skills

    except (json.JSONDecodeError, Exception) as e:
        logger.error("An error occurred while extracting technical skills: %s", e)
        return []
