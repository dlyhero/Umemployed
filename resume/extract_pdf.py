import os
import json
import logging
import dotenv
import pdfplumber
import io
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
from datetime import datetime, date
from django.contrib import messages
from azure.storage.blob import BlobServiceClient
from docx import Document

dotenv.load_dotenv()
api_key = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)
logger = logging.getLogger(__name__)

@login_required(login_url='login')
def upload_resume(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)
        if form.is_valid():
            resume_doc, created = ResumeDoc.objects.get_or_create(user=request.user)
            resume_doc.file = form.cleaned_data['file']
            resume_doc.extracted_text = ''
            resume_doc.extracted_skills.clear()
            resume_doc.save()

            file_path = resume_doc.file.name
            print(f"File path for extraction: {file_path}")

            redirect_url = reverse('extract_text', kwargs={'file_path': file_path})
            return redirect(redirect_url)
        else:
            messages.error(request, 'Invalid form submission. Please try again.')
            return redirect('upload')
    else:
        form = ResumeForm()
    resume_doc = ResumeDoc.objects.filter(user=request.user).first()
    return render(request, 'resume/upload_resume.html', {'form': form, 'resume_doc': resume_doc})

def clean_text(text):
    return text.replace('\x00', '') if text else text

def extract_text(request, file_path):
    account_name = os.getenv('AZURE_ACCOUNT_NAME')
    account_key = os.getenv('AZURE_ACCOUNT_KEY')
    container_name = os.getenv('AZURE_CONTAINER')

    connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    
    blob_name = file_path.replace('https://', '').replace(f"{account_name}.blob.core.windows.net/{container_name}/", '')

    print(f"Trying to access file with blob name: {blob_name}")

    try:
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        file_stream = blob_client.download_blob().readall()

        print(f"File stream size: {len(file_stream)} bytes")

        file_extension = os.path.splitext(blob_name)[1].lower()
        extracted_text = ""

        if file_extension == '.pdf':
            with pdfplumber.open(io.BytesIO(file_stream)) as pdf:
                if pdf.pages:
                    page = pdf.pages[0]
                    extracted_text = page.extract_text() or ""
                    print(f"Extracted text from PDF: {extracted_text[:500]}")
        elif file_extension == '.docx':
            doc = Document(io.BytesIO(file_stream))
            extracted_text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            print(f"Extracted text from DOCX: {extracted_text[:500]}")
        elif file_extension == '.txt':
            extracted_text = file_stream.decode('utf-8')
            print(f"Extracted text from TXT: {extracted_text[:500]}")
        else:
            print(f"Unsupported file extension: {file_extension}")
            return HttpResponse("Unsupported file type", status=400)

        extracted_text = clean_text(extracted_text)
        extracted_details = extract_resume_details(request, extracted_text)
        parse_and_save_details(extracted_details, request.user)

        resume_doc = ResumeDoc.objects.filter(user=request.user).first()
        if resume_doc:
            resume_doc.extracted_text = extracted_text
            resume_doc.save()

            # Fetch the job_title from the Resume model
            resume = Resume.objects.filter(user=request.user).first()
            job_title = resume.job_title if resume and resume.job_title else "Others"

            extract_technical_skills(request, extracted_text, job_title)
            return redirect('update-resume')
        else:
            # If ResumeDoc does not exist, use "Others" as the job_title
            extract_technical_skills(request, extracted_text, "Others")
            return HttpResponse("Error: ResumeDoc not found")

    except Exception as e:
        print("Error during file extraction:", str(e))
        messages.error(request, "An error occurred while processing the resume. Please try again.")
        return HttpResponse("Error: Could not process the file", status=500)

def extract_technical_skills(request, extracted_text, job_title):
    conversation = [
        {
            "role": "user",
            "content": f"Given the following resume details: {extracted_text}, identify and list all the technical skills that can be practically tested during a technical interview. Focus on extracting skills related to hands-on technical knowledge, coding abilities, use of specific software tools, problem-solving skills, and any other competencies that can be demonstrated through practical tests, coding challenges, or problem-solving exercises. Exclude skills that cannot be directly tested in an interview setting, such as soft skills or theoretical knowledge not applicable to practical tasks. Format your output in JSON, organizing the skills under a key named 'Technical Skills'. Each skill should be listed as an element in an array of strings. Ensure that each skill does not comprise more than two words."
        }
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=conversation,
            timeout=120
        )

        response_content = response.choices[0].message.content
        response_dict = json.loads(response_content)
        technical_skills = response_dict.get("Technical Skills", [])
        print(technical_skills)

        resume_doc = ResumeDoc.objects.filter(user=request.user).first()
        if resume_doc:
            for skill in technical_skills:
                skill_obj, created = Skill.objects.get_or_create(name=skill)
                resume_doc.extracted_skills.add(skill_obj)
        
        save_skills_to_database(job_title, technical_skills)
        print('Skills saved to database:', technical_skills)

        return technical_skills

    except (json.JSONDecodeError, Exception) as e:
        logger.error("An error occurred while extracting technical skills: %s", e)
        return []

def extract_resume_details(request, extracted_text):
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
            model="gpt-4",
            messages=conversation,
            timeout=120
        )

        response_content = response.choices[0].message.content
        extracted_details = json.loads(response_content)
        print("Extracted Details from GPT-4:", extracted_details)
        return extracted_details

    except (json.JSONDecodeError, Exception) as e:
        logger.error("An error occurred while extracting resume details: %s", e)
        return {}

def get_case_insensitive(d, key, default=None):
    if not isinstance(d, dict):
        print(f"Expected dictionary, but got {type(d)}: {d}")
        return default
    return next((v for k, v in d.items() if k.lower() == key.lower()), default)

def parse_date(date_str):
    if date_str is None:
        return None
    elif date_str.lower() == "present":
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None

def parse_and_save_details(extracted_details, user):
    name = get_case_insensitive(extracted_details, 'Name', 'Your Name')
    email = get_case_insensitive(extracted_details, 'Email', 'example@email.com')
    phone = get_case_insensitive(extracted_details, 'Phone', '+123456677')

    contact_info, created = ContactInfo.objects.update_or_create(
        user=user,
        defaults={'name': name, 'email': email, 'phone': phone}
    )

    experiences = get_case_insensitive(extracted_details, 'Work Experience', [])
    if isinstance(experiences, list):
        for exp in experiences:
            if isinstance(exp, dict):
                company_name = get_case_insensitive(exp, 'company_name', 'Unknown Company')
                role = get_case_insensitive(exp, 'role', 'Unknown Position')
                start_date = parse_date(exp.get('start_date'))
                end_date = parse_date(exp.get('end_date')) if exp.get('end_date') else None
                if start_date is None:
                    print(f"Invalid start date format for {company_name}. Please provide the date in YYYY-MM-DD format.")
                
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
    else:
        print("Invalid experiences format:", experiences)

    educations = get_case_insensitive(extracted_details, 'Education', [])
    if isinstance(educations, list):
        for edu in educations:
            if isinstance(edu, dict):
                institution_name = get_case_insensitive(edu, 'institution_name', 'Unknown Institution')
                degree = get_case_insensitive(edu, 'degree', 'Unknown Degree')
                field_of_study = get_case_insensitive(edu, 'field_of_study', 'Unknown Field')
                graduation_year = get_case_insensitive(edu, 'graduation_year')
                if graduation_year is not None and str(graduation_year).isdigit():
                    graduation_year = int(graduation_year)
                else:
                    graduation_year = date.today().year
                print("Institution Name:", institution_name)
                print("Degree:", degree)
                print("Field of Study:", field_of_study)
                print("Graduation Year:", graduation_year)
                Education.objects.create(
                    user=user,
                    institution_name=institution_name,
                    degree=degree,
                    field_of_study=field_of_study,
                    graduation_year=graduation_year
                )
                print("Education added - Institution:", institution_name, "Degree:", degree, "Field of Study:", field_of_study, "Graduation Year:", graduation_year)
            else:
                print("Invalid education format:", edu)
    else:
        print("Invalid educations format:", educations)