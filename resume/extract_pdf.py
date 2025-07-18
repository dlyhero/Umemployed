import io
import json
import logging
import os
from datetime import date, datetime

import dotenv
import pdfplumber
from azure.storage.blob import BlobServiceClient
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from docx import Document
from openai import OpenAI
from rest_framework.response import Response

from job.job_description_algorithm import save_skills_to_database
from job.models import Job, Skill, SkillQuestion
from resume.models import Skill, SkillCategory

from .forms import ResumeForm
from .models import *

dotenv.load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
logger = logging.getLogger(__name__)


@login_required(login_url="login")
def upload_resume(request):
    print("upload_resume view called")
    if request.method == "POST":
        print("POST request received")
        form = ResumeForm(request.POST, request.FILES)
        selected_resume_id = request.POST.get("selected_resume")
        print(f"Selected resume ID: {selected_resume_id}")

        if selected_resume_id:
            resume_doc = get_object_or_404(ResumeDoc, id=selected_resume_id, user=request.user)
            file_path = resume_doc.file.name
            print(f"Using previously uploaded file for extraction: {file_path}")

            # Redirect to the next view with the existing extracted text
            redirect_url = reverse("extract_text", kwargs={"file_path": file_path})
            print(f"Redirecting to: {redirect_url}")
            return redirect(redirect_url)

        if form.is_valid():
            print("Form is valid, creating or updating ResumeDoc")
            resume_doc, _ = ResumeDoc.objects.get_or_create(
                user=request.user,
                defaults={"file": form.cleaned_data["file"], "extracted_text": ""},
            )
            resume_doc.file = form.cleaned_data["file"]
            resume_doc.extracted_skills.clear()
            resume_doc.save()

            # Ensure the Resume object is updated
            resume = Resume.objects.filter(user=request.user).first()
            if not resume:
                resume = Resume(user=request.user)
            resume.cv = resume_doc.file  # Link the uploaded file to the Resume model
            resume.save()
            print(f"Resume object updated: {resume}")

            # Set user.has_resume to True
            request.user.has_resume = True
            request.user.save()
            print(f"User {request.user.username} has_resume set to True")

            file_path = resume_doc.file.name
            print(f"File path for extraction: {file_path}")

            redirect_url = reverse("extract_text", kwargs={"file_path": file_path})
            print(f"Redirecting to: {redirect_url}")
            return redirect(redirect_url)
        else:
            print("Form is invalid")
            print(f"Form errors: {form.errors}")
            messages.error(request, "Invalid form submission. Please try again.")
            return redirect("upload")
    else:
        print("GET request received")
        form = ResumeForm()
        resume_docs = ResumeDoc.objects.filter(user=request.user)
        print(f"Found {resume_docs.count()} previously uploaded resumes")
    return render(request, "resume/upload_resume.html", {"form": form, "resume_docs": resume_docs})


def clean_text(text):
    return text.replace("\x00", "") if text else text


def extract_text(request, file_path):
    """
    Extracts raw text from the uploaded resume file.
    """
    account_name = os.getenv("AZURE_ACCOUNT_NAME")
    account_key = os.getenv("AZURE_ACCOUNT_KEY")
    container_name = os.getenv("AZURE_CONTAINER")

    connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)

    blob_name = file_path.replace("https://", "").replace(
        f"{account_name}.blob.core.windows.net/{container_name}/", ""
    )

    print(f"Trying to access file with blob name: {blob_name}")

    try:
        resume_doc = ResumeDoc.objects.filter(user=request.user, file=file_path).first()
        if resume_doc and resume_doc.extracted_text:
            extracted_text = resume_doc.extracted_text
            print(f"Using existing extracted text: {extracted_text[:500]}")
        else:
            blob_client = blob_service_client.get_blob_client(
                container=container_name, blob=blob_name
            )
            file_stream = blob_client.download_blob().readall()

            print(f"File stream size: {len(file_stream)} bytes")

            file_extension = os.path.splitext(blob_name)[1].lower()
            extracted_text = ""

            if file_extension == ".pdf":
                with pdfplumber.open(io.BytesIO(file_stream)) as pdf:
                    if pdf.pages:
                        page = pdf.pages[0]
                        extracted_text = page.extract_text() or ""
                        print(f"Extracted text from PDF: {extracted_text[:500]}")
            elif file_extension == ".docx":
                doc = Document(io.BytesIO(file_stream))
                extracted_text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
                print(f"Extracted text from DOCX: {extracted_text[:500]}")
            elif file_extension == ".txt":
                extracted_text = file_stream.decode("utf-8")
                print(f"Extracted text from TXT: {extracted_text[:500]}")
            else:
                print(f"Unsupported file extension: {file_extension}")
                return Response({"error": "Unsupported file type"}, status=400)

            extracted_text = clean_text(extracted_text)
            if not extracted_text.strip():
                logger.error("Extracted text is empty or invalid after cleaning.")
                return Response(
                    {"error": "Failed to extract meaningful text from the resume."}, status=400
                )

            # Log the extracted text for debugging
            logger.info("Extracted text (cleaned): %s", extracted_text[:500])
            print(f"Extracted text (cleaned): {extracted_text[:500]}")

            # Save the extracted text to the database
            if resume_doc:
                resume_doc.extracted_text = extracted_text
                resume_doc.save()

        # Ensure extracted text is not empty before proceeding
        if not extracted_text.strip():
            logger.error("Extracted text is empty or invalid before sending to OpenAI.")
            return Response({"error": "Extracted text is empty or invalid."}, status=400)

        # Fetch the job_title from the Resume model
        resume = Resume.objects.filter(user=request.user).first()
        job_title = resume.job_title if resume and resume.job_title else "Others"

        # Log the job title and extracted text before calling OpenAI
        logger.info("Job title: %s", job_title)
        logger.info("Extracted text being sent to OpenAI: %s", extracted_text[:500])

        technical_skills = extract_technical_skills(request, extracted_text, job_title)

        return Response(
            {
                "message": "Text extracted successfully.",
                "extracted_text": extracted_text,
                "technical_skills": technical_skills,
            },
            status=200,
        )

    except Exception as e:
        logger.error("Error during file extraction: %s", e)
        return Response({"error": "An error occurred while processing the resume."}, status=500)


def extract_technical_skills(user_or_request, extracted_text, job_title):
    """
    Extracts technical skills from the resume text using OpenAI.
    
    Args:
        user_or_request: Either a User object (for Celery tasks) or request object (for web requests)
        extracted_text: The extracted text from the resume
        job_title: The job title to focus on
    """
    conversation = [
        {
            "role": "user",
            "content": f"Given the following resume details: {extracted_text}, identify and list all the technical skills that can be practically tested during a technical interview. Focus on extracting skills related to hands-on technical knowledge, coding abilities, use of specific software tools, problem-solving skills, and any other competencies that can be demonstrated through practical tests, coding challenges, or problem-solving exercises. Exclude skills that cannot be directly tested in an interview setting, such as soft skills or theoretical knowledge not applicable to practical tasks. Format your output in JSON, organizing the skills under a key named 'Technical Skills'. Each skill should be listed as an element in an array of strings. Ensure that each skill does not comprise more than two words.",
        }
    ]

    try:
        # Log the input being sent to OpenAI
        logger.info("Sending the following prompt to OpenAI: %s", conversation)

        # Try with a shorter timeout first, then fallback to longer timeout if needed
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=conversation,
                timeout=20,  # Set a timeout for the OpenAI API call
            )
        except Exception as e:
            logger.warning(f"First attempt failed with 20s timeout: {str(e)}. Retrying with 40s timeout...")
            response = client.chat.completions.create(
                model="gpt-4",
                messages=conversation,
                timeout=40,  # Fallback timeout
            )

        response_content = response.choices[0].message.content.strip()
        if not response_content:
            raise ValueError("Empty response from OpenAI API")

        # Log the response from OpenAI
        logger.info("Response from OpenAI: %s", response_content)

        response_dict = json.loads(response_content)
        technical_skills = response_dict.get("Technical Skills", [])
        print(technical_skills)

        # Handle both user object (from Celery) and request object (from web)
        if hasattr(user_or_request, 'user'):
            # It's a request object
            user = user_or_request.user
        else:
            # It's a user object
            user = user_or_request
            
        resume_doc = ResumeDoc.objects.filter(user=user).first()
        if resume_doc:
            for skill in technical_skills:
                skill_obj, created = Skill.objects.get_or_create(name=skill)
                resume_doc.extracted_skills.add(skill_obj)

        save_skills_to_database(job_title, technical_skills)
        print("Skills saved to database:", technical_skills)

        return technical_skills

    except (json.JSONDecodeError, ValueError) as e:
        logger.error("An error occurred while extracting technical skills: %s", e)
        return []
    except Exception as e:
        logger.error("Unexpected error while extracting technical skills: %s", e)
        return []


def extract_resume_details(user_or_request, extracted_text):
    """
    Extracts details such as contact information, work experience, and education from the extracted text.
    
    Args:
        user_or_request: Either a User object (for Celery tasks) or request object (for web requests)
        extracted_text: The extracted text from the resume
    """
    try:
        if not extracted_text.strip():
            logger.error("Extracted text is empty or invalid. Skipping API call.")
            return {
                "Name": "Unknown",
                "Email": "unknown@example.com",
                "Phone": "0000000000",
                "Work Experience": [],
                "Education": [],
            }

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
                """,
            }
        ]

        # Log the input sent to the OpenAI API
        logger.info("Sending the following prompt to OpenAI API: %s", conversation)

        # Try with a shorter timeout first, then fallback to longer timeout if needed
        try:
            response = client.chat.completions.create(model="gpt-4", messages=conversation, timeout=30)
        except Exception as e:
            logger.warning(f"First attempt failed with 30s timeout: {str(e)}. Retrying with 60s timeout...")
            response = client.chat.completions.create(model="gpt-4", messages=conversation, timeout=60)

        response_content = response.choices[0].message.content.strip()
        if not response_content or "Sorry" in response_content:
            logger.error("Invalid response from OpenAI API: %s", response_content)
            return {
                "Name": "Unknown",
                "Email": "unknown@example.com",
                "Phone": "0000000000",
                "Work Experience": [],
                "Education": [],
            }

        try:
            extracted_details = json.loads(response_content)
            print("Extracted Details from GPT-4:", extracted_details)
            return extracted_details
        except json.JSONDecodeError as e:
            logger.error("Failed to parse OpenAI API response as JSON: %s", e)
            logger.error("Raw response content: %s", response_content)
            return {
                "Name": "Unknown",
                "Email": "unknown@example.com",
                "Phone": "0000000000",
                "Work Experience": [],
                "Education": [],
            }

    except Exception as e:
        logger.error("Unexpected error while extracting resume details: %s", e)
        logger.info("Falling back to basic text extraction...")
        
        # Fallback: Try to extract basic information using simple text parsing
        try:
            fallback_details = extract_basic_details_fallback(extracted_text)
            return fallback_details
        except Exception as fallback_error:
            logger.error("Fallback extraction also failed: %s", fallback_error)
            return {
                "Name": "Unknown",
                "Email": "unknown@example.com",
                "Phone": "0000000000",
                "Work Experience": [],
                "Education": [],
            }


def extract_basic_details_fallback(extracted_text):
    """
    Fallback function to extract basic details using simple text parsing
    when OpenAI API fails.
    """
    import re
    
    details = {
        "Name": "Unknown",
        "Email": "unknown@example.com", 
        "Phone": "0000000000",
        "Work Experience": [],
        "Education": [],
    }
    
    # Extract email
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, extracted_text)
    if email_match:
        details["Email"] = email_match.group()
    
    # Extract phone number
    phone_pattern = r'(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
    phone_match = re.search(phone_pattern, extracted_text)
    if phone_match:
        details["Phone"] = ''.join(phone_match.groups())
    
    # Try to extract name from first few lines
    lines = extracted_text.split('\n')[:5]
    for line in lines:
        line = line.strip()
        if line and not re.search(r'@|phone|email|resume|cv', line.lower()):
            # Simple heuristic: if line has 2-3 words and no special chars, it might be a name
            words = line.split()
            if 2 <= len(words) <= 3 and all(word.isalpha() for word in words):
                details["Name"] = line
                break
    
    return details


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
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return None


def parse_and_save_details(extracted_details, user):
    """
    Parses and saves extracted details into the database.
    """
    # Parse and save contact information
    name = get_case_insensitive(extracted_details, "Name", "Unknown Name")
    email = get_case_insensitive(extracted_details, "Email", "unknown@example.com")
    phone = get_case_insensitive(extracted_details, "Phone", "0000000000")

    contact_info, created = ContactInfo.objects.update_or_create(
        user=user, defaults={"name": name, "email": email, "phone": phone}
    )
    print(f"Contact Info saved: {contact_info}")

    # Ensure corresponding fields in Resume are updated
    resume = Resume.objects.filter(user=user).first()
    if resume:
        name_parts = name.split(" ", 1)
        resume.first_name = name_parts[0] if len(name_parts) > 0 else ""
        resume.surname = name_parts[1] if len(name_parts) > 1 else ""
        resume.phone = phone
        resume.save()
        print(f"Resume updated with contact info: {resume}")

    # Parse and save work experiences
    experiences = get_case_insensitive(extracted_details, "Work Experience", [])
    if isinstance(experiences, list):
        for exp in experiences:
            if isinstance(exp, dict):
                company_name = get_case_insensitive(exp, "company_name", "Unknown Company")
                role = get_case_insensitive(exp, "role", "Unknown Position")
                start_date = parse_date(exp.get("start_date"))
                end_date = parse_date(exp.get("end_date")) if exp.get("end_date") else None

                WorkExperience.objects.create(
                    user=user,
                    company_name=company_name,
                    role=role,
                    start_date=start_date,
                    end_date=end_date,
                )
                print(f"Work Experience added: {company_name}, {role}, {start_date}, {end_date}")
            else:
                print(f"Invalid work experience format: {exp}")

    # Parse and save education details
    educations = get_case_insensitive(extracted_details, "Education", [])
    if isinstance(educations, list):
        for edu in educations:
            if isinstance(edu, dict):
                institution_name = get_case_insensitive(
                    edu, "institution_name", "Unknown Institution"
                )
                degree = get_case_insensitive(edu, "degree", "Unknown Degree")
                field_of_study = get_case_insensitive(edu, "field_of_study", "Unknown Field")
                graduation_year = get_case_insensitive(edu, "graduation_year")
                if graduation_year is not None and str(graduation_year).isdigit():
                    graduation_year = int(graduation_year)
                else:
                    graduation_year = date.today().year

                Education.objects.create(
                    user=user,
                    institution_name=institution_name,
                    degree=degree,
                    field_of_study=field_of_study,
                    graduation_year=graduation_year,
                )
                print(
                    f"Education added: {institution_name}, {degree}, {field_of_study}, {graduation_year}"
                )
            else:
                print(f"Invalid education format: {edu}")
