import os
import json
import logging
import dotenv
from pypdf import PdfReader
from openai import OpenAI
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from .forms import ResumeForm
from .models import *
from resume.models import SkillCategory, Skill
from job.models import Skill, SkillQuestion, Job
from job.job_description_algorithm import save_skills_to_database 
from . import views
from django.http import HttpResponseRedirect
from django.contrib import messages

dotenv.load_dotenv()
api_key = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)
logger = logging.getLogger(__name__)

def upload_resume(request):
    """
    Handles the upload of resumes.
    """
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            # Check if there's an existing resume for the user
            existing_resume = ResumeDoc.objects.filter(user=request.user).first()
            if existing_resume:
                # If an existing resume is found, update it with the new file
                existing_resume.file = request.FILES['file']
                existing_resume.save()
                # Redirect back to the upload page
                messages.info(request, "Your resume has been updated successfully")
            
            # If no existing resume, proceed with creating a new one
            resume = form.save(commit=False)
            resume.user = request.user
            resume.save()
            # Generate the URL for the extract_text view with the file_path parameter
            file_path = resume.file.url.lstrip('/')
            redirect_url = reverse('extract_text', kwargs={'file_path': file_path})
            # Redirect to the extract_text view
            return HttpResponseRedirect(redirect_url)
        else:
            # If form is not valid, handle the error or redirect as required
            messages.error(request, "Invalid form submission. Please try again.")
            # Redirect back to the upload page
            return HttpResponseRedirect(reverse('upload_resume'))
    else:
        form = ResumeForm()
    return render(request, 'resume/upload_resume.html', {'form': form})


def extract_text(request, file_path):
    """
    Extracts text from a PDF resume file and saves it to the database.
    """
    # Creating a pdf reader object 
    reader = PdfReader(file_path) 

    # Creating a page object 
    page = reader.pages[0] 
    extracted_text = page.extract_text()

    # Get the job title from Resume.job_title based on extracted text
    try:
        resume = Resume.objects.get(user=request.user)
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
    return redirect(views.select_category)


def extract_technical_skills(request, extracted_text, job_title):
    """
    Extracts technical skills from extracted text using GPT-4 and saves them to the database.
    """
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
