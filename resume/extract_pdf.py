import os
import json
import logging
import dotenv
from pypdf import PdfReader
from openai import OpenAI
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from .forms import ResumeForm
from .models import *
from resume.models import SkillCategory, Skill
from job.models import Skill, SkillQuestion, Job
from job.job_description_algorithm import save_skills_to_database 
from . import views
from datetime import datetime,date
from django.contrib import messages

dotenv.load_dotenv()
api_key ="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"
client = OpenAI(api_key=api_key)
logger = logging.getLogger(__name__)

@login_required(login_url='login')
def upload_resume(request):
    """
    Handles the upload of resumes.
    """
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            # Check if a ResumeDoc already exists for the user
            try:
                resume_doc = ResumeDoc.objects.get(user=request.user)
                resume_doc.file = form.cleaned_data['file']  # Update the file
                resume_doc.extracted_text = ''  # Clear the extracted text
                resume_doc.extracted_skills.clear()  # Clear the extracted skills
                resume_doc.save()
            except ResumeDoc.DoesNotExist:
                # Create a new ResumeDoc if it does not exist
                resume_doc = ResumeDoc.objects.create(
                    user=request.user,
                    file=form.cleaned_data['file']
                )

            # Generate the URL for the extract_text view with the file_path parameter
            file_path = resume_doc.file.url.lstrip('/')
            redirect_url = reverse('extract_text', kwargs={'file_path': file_path})

            # Redirect to the extract_text view
            return redirect(redirect_url)
    else:
        form = ResumeForm()
    return render(request, 'resume/upload_resume.html', {'form': form})

def extract_text(request, file_path):
    """
    Extracts text from a PDF resume file and saves it to the database.
    """
    # Creating a pdf reader object 
    job_title = None
    reader = PdfReader(file_path) 

    # Creating a page object 
    page = reader.pages[0] 
    extracted_text = page.extract_text()
    
    # Extract details from the resume text using ChatGPT
    extracted_details = extract_resume_details(request, extracted_text)
    

    # Print the extracted details for debugging
    print("Extracted Details:", extracted_details)
    parse_and_save_details(extracted_details, request.user)


    try:
        resume = Resume.objects.get(user=request.user)
        job_title = resume.job_title
        print("Job title found:", job_title)
    except Resume.DoesNotExist:
        print("Resume not found for extracted text:", extracted_text)
        messages.warning(request, "This failed please try again!")

    # Save the extracted text to the database
    try:
        print("Searching for ResumeDoc with file path:", file_path)
        resume_doc = ResumeDoc.objects.get(user=request.user)
        print("ResumeDoc found:", resume_doc)
        resume_doc.extracted_text = extracted_text
        resume_doc.save()
        print("Extracted text saved to ResumeDoc")

        # Process and save the extracted details to the database or perform other necessary actions
        # For example, you can save the extracted details to appropriate database models based on your models

        # Redirect to the appropriate view
        extract_technical_skills(request, extracted_text, job_title)
        return redirect(views.update_resume)


    except ResumeDoc.DoesNotExist:
        print("ResumeDoc not found for file path:", file_path)
        extract_technical_skills(request, extracted_text, job_title)
        return HttpResponse("Error: ResumeDoc not found")
    return redirect(views.update_resume)



def extract_technical_skills(request, extracted_text, job_title):
    """
    Extracts technical skills from extracted text using gpt-4-turbo-preview and saves them to the database.
    """
    conversation = [
        {
            "role": "user",
            "content": f"Given the following resume details: {extracted_text}, identify and list all the technical skills that can be practically tested during a technical interview. Focus on extracting skills related to hands-on technical knowledge, coding abilities, use of specific software tools, problem-solving skills, and any other competencies that can be demonstrated through practical tests, coding challenges, or problem-solving exercises. Exclude skills that cannot be directly tested in an interview setting, such as soft skills or theoretical knowledge not applicable to practical tasks. Format your output in JSON, organizing the skills under a key named 'Technical Skills'. Each skill should be listed as an element in an array of strings. Ensure that each skill does not comprise more than two words."
        }
    ]

    try:
        # Call gpt-4-turbo-preview to generate technical skills based on resume data
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=conversation,
            timeout=120  # Extended timeout to 120 seconds
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

    

def extract_resume_details(request, extracted_text):
    """
    Extracts contact information, work experience, and education details from the extracted text of a resume using ChatGPT.
    """
    try:
        conversation = [
            {
                "role": "user",
                "content": f"""
                    Given the following resume details: {extracted_text}, extract and list the contact information, work experience, and education details. 
                    Focus on identifying fields such as:
                    - Name
                    - Email
                    - Phone
                    - Work Experience (company_name, role, start_date, end_date)
                    - Education (institution_name, degree, field_of_study, graduation_year)
                    Format the output in JSON with appropriate keys.
                """
            }
        ]

        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=conversation,
            timeout=120
        )

        response_content = response.choices[0].message.content
        extracted_details = json.loads(response_content)
        return extracted_details

    except (json.JSONDecodeError, Exception) as e:
        logger.error("An error occurred while extracting resume details: %s", e)
        return {}


def get_case_insensitive(d, key, default=None):
    """ Helper function to perform case-insensitive key lookup in a dictionary. """
    return next((v for k, v in d.items() if k.lower() == key.lower()), default)

from datetime import datetime, date
# Function to parse dates with special values like "Present"
# Function to parse dates with special values like "Present"
def parse_date(date_str):
    if date_str is None:
        return None
    elif date_str.lower() == "present":
        return None  # or you can return today's date: return date.today()
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None  # Handle invalid date format gracefully


def parse_and_save_details(extracted_details, user):
    # Extract basic information
    name = get_case_insensitive(extracted_details, 'Name', 'Your Name')
    email = get_case_insensitive(extracted_details, 'Email', 'example@email.com')
    phone = get_case_insensitive(extracted_details, 'Phone', '+123456677')

    print("Extracted Name:", name)
    print("Extracted Email:", email)
    print("Extracted Phone:", phone)

    # Create or update ContactInfo instance
    contact_info, created = ContactInfo.objects.update_or_create(
        user=user,
        defaults={'name': name, 'email': email, 'phone': phone}
    )

    print("ContactInfo saved:", contact_info)

    # Extract work experiences
    experiences = get_case_insensitive(extracted_details, 'Work Experience', [])
    for exp in experiences:
        if isinstance(exp, dict):
            company_name = get_case_insensitive(exp, 'company_name', 'Unknown Company')
            role = get_case_insensitive(exp, 'role', 'Unknown Position')
            start_date = parse_date(exp.get('start_date'))
            end_date = parse_date(exp.get('end_date')) if exp.get('end_date') else None
            if start_date is None:
                print(f"Invalid start date format for {company_name}. Please provide the date in YYYY-MM-DD format.")
            
            # Create WorkExperience instance
            WorkExperience.objects.create(
                user=user,
                company_name=company_name,
                role=role,
                start_date=start_date,
                end_date=end_date
            )
            print("Work Experience added - Company:", company_name, "Position:", role, "Start Date:", start_date, "End Date:", end_date)
        else:
            print("Invalid experience format:", exp)

    # Extract education details
    educations = get_case_insensitive(extracted_details, 'Education', [])
    for edu in educations:
        institution_name = get_case_insensitive(edu, 'institution_name', 'Unknown Institution')
        degree = get_case_insensitive(edu, 'degree', 'Unknown Degree')
        field_of_study = get_case_insensitive(edu, 'field_of_study', 'Unknown Field')
        graduation_year = get_case_insensitive(edu, 'graduation_year')
        if graduation_year is not None and str(graduation_year).isdigit():
            graduation_year = int(graduation_year)
        else:
            graduation_year = date.today().year  # Set to the current year if 'graduation_year' is not clear
        print("Institution Name:", institution_name)
        print("Degree:", degree)
        print("Field of Study:", field_of_study)
        print("Graduation Year:", graduation_year)
        # Create Education instance
        Education.objects.create(
            user=user,
            institution_name=institution_name,
            degree=degree,
            field_of_study=field_of_study,
            graduation_year=graduation_year
        )
        print("Education added - Institution:", institution_name, "Degree:", degree, "Field of Study:", field_of_study, "Graduation Year:", graduation_year)
