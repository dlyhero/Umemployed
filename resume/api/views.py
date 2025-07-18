import json
import logging
import os  # Add this import for accessing environment variables

import openai  # Assuming you use OpenAI or similar for AI enhancement
from azure.storage.blob import BlobServiceClient
from django.conf import settings
from django.db.models import Max  # Import Max for querying the latest resume
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from job.models import Job  # Import Job model
from notifications.models import Notification  # Add this import
from resume.extract_pdf import (  # Import existing functions
    extract_resume_details,
    extract_technical_skills,
    extract_text,
    parse_and_save_details,
)
from resume.models import (
    ContactInfo,
    Education,
    EnhancedResume,
    Experience,
    Language,
    ProfileView,
    Resume,
    ResumeAnalysis,
    ResumeDoc,
    Skill,
    SkillCategory,
    Transcript,
    UserLanguage,
    WorkExperience,
)
from resume.transcript_job_title import extract_transcript_text  # Import the old function
from resume.views import display_matching_jobs, update_resume, update_resume_view, upload_resume
from transactions.models import Subscription

from .serializers import (
    AboutSerializer,
    ContactInfoSerializer,
    CountriesSerializer,
    EducationListSerializer,
    EducationSerializer,
    EnhancedResumeSerializer,
    ExperienceListSerializer,
    ExperienceSerializer,
    LanguageSerializer,
    PersonalDetailsSerializer,
    ProfileViewSerializer,
    ResumeAnalysisSerializer,
    ResumeSerializer,
    SkillCategorySerializer,
    SkillListSerializer,
    SkillSerializer,
    SkillsListSerializer,
    UserLanguageSerializer,
    WorkExperienceSerializer,
)

logger = logging.getLogger(__name__)


@api_view(["POST"])
def update_resume_api(request):
    """
    Updates the resume for the authenticated user.

    This endpoint references the existing `update_resume` function in the `resume` app.
    It accepts a POST request with the necessary data to update the user's resume.

    Request Body:
        {
            "first_name": "John",
            "last_name": "Doe",
            "job_title": "Software Engineer",
            "phone": "+1234567890",
            "description": "Experienced software engineer with expertise in backend development."
        }

    Response:
        {
            "message": "Resume updated successfully."
        }
    """
    try:
        # Call the existing update_resume function
        response = update_resume(request)

        # Check if the response is an HTML response
        if isinstance(response, HttpResponse) and response.status_code == 200:
            # Notify user of resume update
            Notification.objects.create(
                user=request.user,
                notification_type=Notification.PROFILE_UPDATED,
                message="Your resume has been updated successfully.",
            )
            return Response({"message": "Resume updated successfully."}, status=200)
        else:
            return Response({"error": "Failed to update resume."}, status=500)
    except Exception as e:
        return Response({"error": f"An error occurred: {str(e)}"}, status=500)


@api_view(["GET"])
def resume_details_api(request):
    """
    Retrieves details of the resume for the currently logged-in user.
    If multiple resumes exist, it returns the most recently created one.

    Response:
        {
            "id": 1,
            "user": 1,
            "first_name": "John",
            "surname": "Doe",
            ...
        }
    """
    user = request.user
    try:
        # Get the latest resume for the logged-in user
        resume = Resume.objects.filter(user=user).order_by("-created_at").first()
        if not resume:
            return Response({"error": "No resume found for the current user."}, status=404)

        # Serialize the resume object
        serializer = ResumeSerializer(resume)
        return Response(serializer.data, status=200)
    except Exception as e:
        return Response({"error": f"An error occurred: {str(e)}"}, status=500)


@api_view(["GET"])
def matching_jobs_api(request):
    """
    Displays jobs matching the user's resume.

    This endpoint references the existing `display_matching_jobs` function in the `resume` app.

    Response:
        [
            {
                "job_id": 1,
                "title": "Backend Developer",
                "company": "TechCorp",
                ...
            }
        ]
    """
    return display_matching_jobs(request)


@api_view(["POST"])
def upload_resume_api(request):
    """
    Uploads a resume file for the authenticated user and triggers the extraction process.

    Request Body (Form-Data):
        file: Resume file (PDF, DOCX, or TXT).

    Response:
        {
            "message": "Resume uploaded and processed successfully.",
            "extracted_text": "Extracted text from the resume.",
            "technical_skills": [...],
            "extracted_details": {...}
        }
    """
    if "file" not in request.FILES:
        return Response({"error": "The 'file' field is required."}, status=400)

    file = request.FILES["file"]
    user = request.user

    # Save the file to the ResumeDoc model
    resume_doc = ResumeDoc(user=user, file=file)
    try:
        resume_doc.save()
        logger.info(f"File uploaded to Azure Blob Storage: {resume_doc.file.name}")

        # Ensure the Resume object is updated
        resume = Resume.objects.filter(user=user).first()
        if not resume:
            resume = Resume(user=user)
        resume.cv = resume_doc.file  # Link the uploaded file to the Resume model
        resume.save()
        logger.info(f"Resume object updated: {resume}")

        # Set user.has_resume to True
        user.has_resume = True
        user.save()
        logger.info(f"User {user.username} has_resume set to True")
        # Notify user of resume upload
        Notification.objects.create(
            user=user,
            notification_type=Notification.PROFILE_UPDATED,
            message="Your resume has been uploaded and processed successfully.",
        )
    except Exception as e:
        logger.error(f"Failed to upload file: {str(e)}")
        return Response({"error": f"Failed to upload file: {str(e)}"}, status=500)

    # Perform text extraction and parsing using the extract_pdf functions
    try:
        file_path = resume_doc.file.name  # Use the file name as the file_path

        # Step 1: Extract raw text from the resume
        extracted_text_response = extract_text(request, file_path)
        if extracted_text_response.status_code != 200:
            return extracted_text_response

        extracted_text = extracted_text_response.data.get("extracted_text", "")
        if not extracted_text.strip():
            logger.error("Extracted text is empty or invalid after calling extract_text.")
            return Response(
                {"error": "Failed to extract meaningful text from the resume."}, status=400
            )

        logger.info("Extracted text received in API: %s", extracted_text[:500])

        # Save the extracted text immediately
        resume_doc.extracted_text = extracted_text
        resume_doc.save()

        # Step 2: Extract and save details using extract_resume_details and parse_and_save_details
        # Set a reasonable timeout for the entire processing
        import threading
        import time
        
        extracted_details = {
            "Name": "Unknown",
            "Email": "unknown@example.com",
            "Phone": "0000000000",
            "Work Experience": [],
            "Education": [],
        }
        
        technical_skills = []
        
        # Process with timeout
        def process_resume():
            nonlocal extracted_details, technical_skills
            try:
                extracted_details = extract_resume_details(request, extracted_text)
                parse_and_save_details(extracted_details, user)
            except Exception as e:
                logger.error(f"Error extracting resume details: {str(e)}")
            
            try:
                job_title = resume.job_title if resume.job_title else "Others"
                technical_skills = extract_technical_skills(request, extracted_text, job_title)
            except Exception as e:
                logger.error(f"Error extracting technical skills: {str(e)}")
        
        # Run processing in a thread with timeout
        processing_thread = threading.Thread(target=process_resume)
        processing_thread.start()
        processing_thread.join(timeout=90)  # 90 second timeout
        
        if processing_thread.is_alive():
            logger.warning("Resume processing timed out, returning basic results")
            # The thread will continue running in background, but we return what we have

        return Response(
            {
                "message": "Resume uploaded and processed successfully.",
                "extracted_text": extracted_text,
                "technical_skills": technical_skills,
                "extracted_details": extracted_details,
            },
            status=200,
        )
    except Exception as e:
        logger.error("Error in upload_resume_api: %s", e)
        return Response({"error": f"Failed to process resume: {str(e)}"}, status=500)


@api_view(["POST"])
def analyze_resume_api(request):
    """
    Analyzes the uploaded resume and provides feedback.

    This endpoint references the existing `update_resume_view` function in the `resume` app.

    Response:
        {
            "overall_score": 85.5,
            "criteria_scores": {
                "formatting": 90,
                "skills": 80
            },
            "improvement_suggestions": {
                "skills": "Add more technical skills."
            }
        }
    """
    return update_resume_view(request)


from resume.extract_pdf import extract_text  # Import the existing extract_text function


@api_view(["POST"])
def upload_transcript_api(request):
    """
    Handles transcript upload for the authenticated user and triggers processing.

    Request Body (Form-Data):
        file: Transcript file.

    Response:
        {
            "message": "Transcript uploaded and processed successfully.",
            "extracted_text": "Extracted text from the transcript.",
            "job_title": "Suggested job title.",
            "reasoning": "Reasoning based on the transcript analysis."
        }
    """
    if "file" not in request.FILES:
        return Response({"error": "The 'file' field is required."}, status=400)

    file = request.FILES["file"]
    user = request.user

    # Save the file to the Transcript model
    transcript = Transcript(user=user, file=file)
    try:
        transcript.save()
        print(f"Transcript uploaded: {transcript.file.name}")

        # Upload the file to Azure Blob Storage
        account_name = os.getenv("AZURE_ACCOUNT_NAME")
        account_key = os.getenv("AZURE_ACCOUNT_KEY")
        container_name = os.getenv("AZURE_CONTAINER")

        connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(
            container=container_name, blob=transcript.file.name
        )

        # Upload the file
        with file.open("rb") as data:
            blob_client.upload_blob(data, overwrite=True)
        print(f"File uploaded to Azure Blob Storage: {transcript.file.name}")

    except Exception as e:
        return Response({"error": f"Failed to upload transcript: {str(e)}"}, status=500)

    # Perform text extraction and additional processing
    try:
        # Call the old extract_transcript_text function
        file_path = transcript.file.name  # Use the file name as the file_path
        print(f"Processing file with path: {file_path}")

        # Call the old function to process the transcript
        extract_transcript_text(request, file_path)

        # Refresh the transcript object to get updated fields
        transcript.refresh_from_db()

        # Return the processed response
        return Response(
            {
                "message": "Transcript uploaded and processed successfully.",
                "extracted_text": transcript.extracted_text,
                "job_title": transcript.job_title,
                "reasoning": transcript.reasoning,
            },
            status=200,
        )
    except Exception as e:
        return Response({"error": f"Failed to process transcript: {str(e)}"}, status=500)


@api_view(["POST"])
def extract_transcript_api(request):
    """
    Extracts text from an uploaded transcript.

    Request Body:
        {
            "transcript_id": 1
        }

    Response:
        {
            "extracted_text": "This is the extracted text from the transcript."
        }
    """
    transcript_id = request.data.get("transcript_id")
    transcript = get_object_or_404(Transcript, id=transcript_id)
    extracted_text = transcript.extracted_text  # Assuming text is already extracted
    return Response({"extracted_text": extracted_text})


class SkillViewSet(ModelViewSet):
    """
    Handles CRUD operations for user skills.
    - GET: Retrieve all skills for the logged-in user.
    - POST: Add a new skill for the logged-in user.
    - PUT/PATCH: Update an existing skill for the logged-in user.
    - DELETE: Delete a skill for the logged-in user.
    """

    serializer_class = SkillSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return Skill.objects.none()
        return Skill.objects.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        # Return list of {id, name}
        data = [{"id": skill.id, "name": skill.name} for skill in queryset]
        return Response(data)


class EducationViewSet(ModelViewSet):
    """
    Handles CRUD operations for user education records.
    - GET: Retrieve all education records for the logged-in user.
    - POST: Add a new education record for the logged-in user.
    - PUT/PATCH: Update an existing education record for the logged-in user.
    - DELETE: Delete an education record for the logged-in user.
    """

    serializer_class = EducationSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return Education.objects.none()
        return Education.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically set the user to the currently authenticated user
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        # Ensure the user field is not changed during updates
        serializer.save(user=self.request.user)


class ExperienceViewSet(ModelViewSet):
    """
    Handles CRUD operations for user work experiences.
    - GET: Retrieve all work experiences for the logged-in user.
    - POST: Add a new work experience for the logged-in user.
    - PUT/PATCH: Update an existing work experience for the logged-in user.
    - DELETE: Delete a work experience for the logged-in user.
    """

    serializer_class = ExperienceSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return Experience.objects.none()
        return Experience.objects.filter(user=self.request.user)


class ContactInfoViewSet(ModelViewSet):
    """
    Handles CRUD operations for user contact information.
    - GET: Retrieve all contact information for the logged-in user.
    - POST: Add new contact information for the logged-in user.
    - PUT/PATCH: Update existing contact information for the logged-in user.
    - DELETE: Delete contact information for the logged-in user.
    """

    serializer_class = ContactInfoSerializer

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return ContactInfo.objects.none()
        return ContactInfo.objects.filter(user=self.request.user)


class WorkExperienceViewSet(ModelViewSet):
    """
    Handles CRUD operations for user work experiences.
    - GET: Retrieve all work experiences for the logged-in user.
    - POST: Add a new work experience for the logged-in user.
    - PUT/PATCH: Update an existing work experience for the logged-in user.
    - DELETE: Delete a work experience for the logged-in user.
    """

    serializer_class = WorkExperienceSerializer

    def get_queryset(self):
        # Short-circuit for schema generation or unauthenticated user
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return WorkExperience.objects.none()
        return WorkExperience.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # Automatically set the user to the currently authenticated user
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        # Ensure the user field is not changed during updates
        serializer.save(user=self.request.user)


class LanguageViewSet(ModelViewSet):
    """
    Handles CRUD operations for user languages.
    - GET: Retrieve all languages for the logged-in user.
    - POST: Add a new language for the logged-in user.
    - PUT/PATCH: Update an existing language for the logged-in user.
    - DELETE: Delete a language for the logged-in user.
    """

    serializer_class = UserLanguageSerializer

    def get_queryset(self):
        # Short-circuit for schema generation or unauthenticated user
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return UserLanguage.objects.none()
        return UserLanguage.objects.filter(user_profile__user=self.request.user)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        # Automatically set the user_profile to the currently authenticated user's profile
        user_profile = getattr(self.request.user, "userprofile", None)
        if not user_profile:
            # Create UserProfile if it doesn't exist
            from resume.models import UserProfile
            user_profile = UserProfile.objects.create(
                user=self.request.user,
                country="US"  # Default country
            )
        serializer.save(user_profile=user_profile)

    def perform_update(self, serializer):
        user_profile = getattr(self.request.user, "userprofile", None)
        if not user_profile:
            # Create UserProfile if it doesn't exist
            from resume.models import UserProfile
            user_profile = UserProfile.objects.create(
                user=self.request.user,
                country="US"  # Default country
            )
        serializer.save(user_profile=user_profile)


class LanguageListView(ListAPIView):
    """
    Read-only endpoint to fetch all available languages (for dropdowns).
    """

    queryset = Language.objects.all()
    serializer_class = LanguageSerializer
    permission_classes = [AllowAny]


class ProficiencyChoicesAPIView(APIView):
    """
    Get list of all proficiency levels for language dropdown selections.
    
    **Response:**
    ```json
    {
        "proficiency_levels": [
            {
                "value": "beginner",
                "label": "Beginner"
            },
            {
                "value": "intermediate", 
                "label": "Intermediate"
            },
            {
                "value": "advanced",
                "label": "Advanced"
            },
            {
                "value": "native",
                "label": "Native"
            }
        ]
    }
    ```
    """
    permission_classes = []  # No authentication required for proficiency choices
    
    def get(self, request):
        from resume.models import UserLanguage
        
        proficiency_choices = [
            {"value": choice[0], "label": choice[1]} 
            for choice in UserLanguage.PROFICIENCY_CHOICES
        ]
        
        return Response({
            "proficiency_levels": proficiency_choices
        })


@api_view(["GET"])
def resume_analyses_api(request):
    """
    Retrieves all resume analyses.

    Response:
        [
            {
                "id": 1,
                "overall_score": 85.5,
                ...
            }
        ]
    """
    analyses = ResumeAnalysis.objects.all()
    serializer = ResumeAnalysisSerializer(analyses, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def profile_views_api(request):
    """
    Retrieves all profile views.

    Response:
        [
            {
                "id": 1,
                "viewed_at": "2023-10-01T12:00:00Z"
            }
        ]
    """
    profile_views = ProfileView.objects.all()
    serializer = ProfileViewSerializer(profile_views, many=True)
    return Response(serializer.data)


from resume.models import ResumeAnalysis  # Import the ResumeAnalysis model
from resume.resume_analysis import analyze_resume  # Import the old function


@api_view(["POST"])
def resume_analysis_api(request):
    """
    Analyzes an uploaded resume file and provides feedback.

    Request Body (Form-Data):
        file: Resume file (PDF, DOCX, or TXT).

    Response:
        {
            "overall_score": 85.5,
            "criteria_scores": {
                "formatting": 90,
                "skills": 80
            },
            "improvement_suggestions": {
                "skills": "Add more technical skills."
            }
        }
    """
    if "file" not in request.FILES:
        return Response({"error": "The 'file' field is required."}, status=400)

    file = request.FILES["file"]
    user = request.user

    # Save the file to the ResumeDoc model
    resume_doc = ResumeDoc(user=user, file=file)
    try:
        resume_doc.save()
        print(f"File uploaded to Azure Blob Storage: {resume_doc.file.name}")
    except Exception as e:
        return Response({"error": f"Failed to upload file: {str(e)}"}, status=500)

    # Extract text from the uploaded file
    try:
        file_path = resume_doc.file.name  # Use the file name as the file_path
        extract_text(request, file_path)  # Call the extract_text function to extract text
        resume_doc.refresh_from_db()  # Refresh the model to get updated extracted_text
        extracted_text = resume_doc.extracted_text
    except Exception as e:
        return Response({"error": f"Failed to extract text: {str(e)}"}, status=500)

    # Perform resume analysis
    try:
        # Call the old analyze_resume function with extracted_text
        analysis_results = analyze_resume(resume_doc, extracted_text)

        # Save the analysis results to the database
        ResumeAnalysis.objects.create(
            user=resume_doc.user,
            resume=resume_doc,
            overall_score=analysis_results["overall_score"],
            criteria_scores=analysis_results["criteria_scores"],
            improvement_suggestions=analysis_results["improvement_suggestions"],
        )

        # Return the analysis results
        return Response(
            {
                "overall_score": analysis_results["overall_score"],
                "criteria_scores": analysis_results["criteria_scores"],
                "improvement_suggestions": analysis_results["improvement_suggestions"],
            },
            status=200,
        )
    except Exception as e:
        return Response({"error": f"An error occurred: {str(e)}"}, status=500)


from rest_framework.views import APIView


class SkillCategoryListView(APIView):
    """
    Fetches all items in the SkillCategory model, sorted alphabetically.

    Response:
        [
            {
                "id": 1,
                "name": "Backend Development"
            },
            {
                "id": 2,
                "name": "Frontend Development"
            },
            ...
        ]
    """

    def get(self, request):
        skill_categories = SkillCategory.objects.all().order_by("name")  # Sort alphabetically
        serializer = SkillCategorySerializer(skill_categories, many=True)
        return Response(serializer.data)


@api_view(["GET"])
def user_profile_details_api(request, user_id):
    """
    Retrieves a user's skills (from Resume), contact information, work experience, and languages by user ID.

    Response:
        {
            "skills": [...],
            "contact_info": {...},
            "work_experience": [...],
            "languages": [...],
            "profile_image": "url_to_image",
            "description": "User description",
            "education": [...]
        }
    """
    try:
        # Fetch user's skills from the Resume model
        resume = Resume.objects.filter(user_id=user_id).first()
        if resume:
            skills_serializer = SkillSerializer(resume.skills.all(), many=True)
        else:
            skills_serializer = []

        # Fetch user's contact information
        contact_info = ContactInfo.objects.filter(user_id=user_id).first()
        contact_info_serializer = ContactInfoSerializer(contact_info)

        # Fetch user's work experience (return all, not just one)
        work_experience = WorkExperience.objects.filter(user_id=user_id)
        work_experience_serializer = WorkExperienceSerializer(work_experience, many=True)

        # Fetch user's education (return all, not just one)
        educations = Education.objects.filter(user_id=user_id)
        education_serializer = EducationSerializer(educations, many=True)

        # Fetch user's languages
        user_languages = UserLanguage.objects.filter(user_profile__user_id=user_id)
        languages = [user_language.language for user_language in user_languages]
        languages_serializer = LanguageSerializer(languages, many=True)

        # Include profile_image and description from Resume
        profile_image = resume.profile_image.url if resume and resume.profile_image else None
        description = resume.description if resume else None

        return Response(
            {
                "skills": skills_serializer.data if resume else [],
                "contact_info": contact_info_serializer.data if contact_info else None,
                "work_experience": work_experience_serializer.data,
                "education": education_serializer.data,
                "languages": languages_serializer.data,
                "profile_image": profile_image,
                "description": description,
            },
            status=200,
        )
    except Exception as e:
        return Response({"error": f"An error occurred: {str(e)}"}, status=500)


from resume.models import ResumeEnhancementTask
from resume.tasks import enhance_resume_task


@api_view(["POST"])
def enhance_resume_api(request, job_id):
    """
    Initiates asynchronous resume enhancement for a specific job description.

    Request Body (Form-Data):
        file: Resume file (PDF, DOCX, or TXT).

    URL Parameter:
        job_id: ID of the job the user is applying for.

    Response:
        {
            "message": "Resume enhancement initiated successfully.",
            "task_id": "uuid-string",
            "status_url": "/api/resume/enhancement-status/uuid-string/"
        }
    """
    # Subscription check: require at least standard or premium
    user = request.user
    subscription = (
        Subscription.objects.filter(user=user, user_type="user", is_active=True)
        .order_by("-started_at")
        .first()
    )
    if not subscription or subscription.tier not in ["standard", "premium"]:
        return Response(
            {
                "error": "You need a Standard or Premium subscription to use the resume enhancer. Please upgrade your plan."
            },
            status=403,
        )

    file = request.FILES.get("file")
    user = request.user

    if not file:
        return Response({"error": "The 'file' field is required."}, status=400)

    # Save the file to ResumeDoc
    resume_doc = ResumeDoc(user=user, file=file)
    try:
        resume_doc.save()
    except Exception as e:
        return Response({"error": f"Failed to upload file: {str(e)}"}, status=500)

    # Extract resume text
    try:
        file_path = resume_doc.file.name
        extracted_text_response = extract_text(request, file_path)
        if extracted_text_response.status_code != 200:
            return extracted_text_response
        resume_text = extracted_text_response.data.get("extracted_text", "")
        if not resume_text.strip():
            return Response(
                {"error": "Failed to extract meaningful text from the resume."}, status=400
            )
    except Exception as e:
        return Response({"error": f"Failed to extract text: {str(e)}"}, status=500)

    # Fetch job description
    try:
        job = Job.objects.get(id=job_id)
        job_description = str(job.description)
    except Job.DoesNotExist:
        return Response({"error": "Job not found."}, status=404)

    # Remove fields not needed per the system prompt (focus on ATS, summary, experience, and core sections)
    section_str = "full_name, email, phone, linkedin, location, summary, skills, experience, education, certifications"
    # --- Updated system prompt to instruct AI to return lists for education, experience, and certifications ---
    system_prompt = (
        "YOU ARE A WORLD-CLASS RESUME ENHANCEMENT AGENT SPECIALIZED IN TAILORING RESUMES TO MATCH SPECIFIC JOB DESCRIPTIONS. "
        "YOUR TASK IS TO TRANSFORM A PARSED RESUME TO ALIGN PERFECTLY WITH THE PROVIDED JOB DESCRIPTION, OPTIMIZING FOR ATS (APPLICANT TRACKING SYSTEM) PARSING AND RELEVANCY.\n\n"
        "###INSTRUCTIONS###\n"
        "UPDATE ONLY THE SUMMARY AND EXPERIENCE SECTIONS BASED ON THE JOB DESCRIPTION,\n"
        f"ENSURE THE FINAL RESUME INCLUDES ONLY THE FOLLOWING SECTIONS: {section_str},\n"
        "FORMAT OUTPUT USING ATS-COMPATIBLE STRUCTURE: clean headings, no graphics/tables, consistent formatting,\n"
        "INTEGRATE RELEVANT KEYWORDS, SKILLS, TOOLS, AND PHRASES DIRECTLY FROM THE JOB DESCRIPTION,\n"
        "PRESERVE THE CANDIDATE'S ORIGINAL ACCOMPLISHMENTS WHILE REPHRASING TO ALIGN WITH JOB REQUIREMENTS,\n"
        "MAINTAIN PROFESSIONAL, CONCISE LANGUAGE FOCUSED ON IMPACT AND RESULTS,\n"
        "FOR THE 'skills' SECTION, GROUP/CATEGORIZE THE SKILLS INTO RELEVANT CATEGORIES (e.g., 'Programming Languages', 'Machine Learning', 'Software', etc.) "
        "AND RETURN THEM AS AN OBJECT WHERE EACH KEY IS A CATEGORY AND THE VALUE IS A LIST OF SKILLS IN THAT CATEGORY. "
        'EXAMPLE: {"Programming Languages": ["Python", "SQL"], "Machine Learning": ["KNN", "XGBoost"]}\n'
        "FOR THE 'education' SECTION, RETURN A LIST OF ALL EDUCATION ENTRIES FOUND, NOT JUST ONE. "
        "FOR THE 'experience' SECTION, RETURN A LIST OF ALL WORK EXPERIENCE ENTRIES FOUND, NOT JUST ONE. "
        "FOR THE 'certifications' SECTION, RETURN A LIST OF ALL CERTIFICATIONS FOUND, NOT JUST ONE. "
        "EACH ENTRY IN 'education', 'experience', or 'certifications' SHOULD BE AN OBJECT WITH RELEVANT FIELDS (e.g., institution, degree, years for education; company, role, dates for experience; name, issuer, year for certifications).\n\n"
        "###CHAIN OF THOUGHTS###\n"
        "UNDERSTAND: READ AND COMPREHEND BOTH THE PARSED RESUME AND JOB DESCRIPTION,\n"
        "BASICS: IDENTIFY THE JOB TITLE, KEY RESPONSIBILITIES, REQUIRED SKILLS, AND INDUSTRY CONTEXT,\n"
        "BREAK DOWN: DECONSTRUCT THE JOB DESCRIPTION INTO A LIST OF DESIRED QUALIFICATIONS, TOOLS, AND EXPERIENCES,\n"
        "ANALYZE: COMPARE THE JOB REQUIREMENTS TO THE CANDIDATE'S EXPERIENCE, IDENTIFYING ALIGNMENT AND GAPS,\n"
        "BUILD: REWRITE THE SUMMARY TO EMPHASIZE RELEVANT SKILLS, TOOLS, AND INDUSTRY EXPERIENCE\n"
        "REWRITE EACH BULLET IN THE EXPERIENCE SECTION TO HIGHLIGHT MATCHING SKILLS AND IMPACT,\n"
        "EDGE CASES: IF A MATCHING TOOL/SKILL IS MISSING, PRIORITIZE GENERAL BUT RELATED TRANSFERABLE LANGUAGE,\n"
        f"FINAL ANSWER: RETURN ONLY THE UPDATED RESUME CONTAINING SECTIONS: {section_str},\n\n"
        "###WHAT NOT TO DO###\n"
        f"NEVER INCLUDE SECTIONS OUTSIDE THE ALLOWED LIST: {section_str},\n"
        "NEVER COPY-PASTE LARGE CHUNKS FROM THE JOB DESCRIPTION WITHOUT ADAPTATION,\n"
        'NEVER USE GENERIC, VAGUE LANGUAGE (E.G., "responsible for", "worked on"),\n'
        "NEVER INCLUDE GRAPHICS, COLUMNS, IMAGES, OR TABLES (NON-ATS COMPATIBLE),\n"
        "NEVER OMIT RELEVANT KEYWORDS OR INDUSTRY TERMINOLOGY FOUND IN THE JOB DESCRIPTION,\n"
        "NEVER INTRODUCE FABRICATED INFORMATION OR FAKE EXPERIENCES,\n\n"
        "###FEW-SHOT EXAMPLES###\n"
        "Original Experience Bullet:\n"
        "Led a team of developers to build internal tools.\n\n"
        "Job Description Requirement:\n"
        "Experience with Agile methodologies and CI/CD pipelines.\n\n"
        "Optimized Bullet:\n"
        "Led a cross-functional Agile team to develop internal tools, integrating CI/CD pipelines for accelerated deployment cycles.\n"
    )

    # Compose the user prompt
    user_prompt = (
        "Given the following resume text and job description, rewrite and enhance the resume so that it is smooth, well-structured, "
        "and tailored to match the job description as closely as possible. "
        "Ensure the resume highlights relevant skills, experience, and qualifications that fit the job. "
        "Return only a valid JSON object with the allowed sections.\n\n"
        f"Resume Text:\n{resume_text}\n\n"
        f"Job Description:\n{job_description}\n"
    )

    # Validate job exists and initiate async processing
    try:
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        return Response({"error": "Job not found."}, status=404)

    # Create task record and initiate background processing
    try:
        from resume.models import ResumeEnhancementTask
        from resume.tasks import enhance_resume_task

        # Create task tracking record first
        task_record = ResumeEnhancementTask.objects.create(
            user=user, job=job, task_id="temp", status="pending"  # Temporary, will be updated
        )

        # Start the Celery task with the record ID
        task_result = enhance_resume_task.delay(user.id, job_id, resume_text, task_record.id)

        # Update the task record with the actual task ID
        task_record.task_id = task_result.id
        task_record.save()

        return Response(
            {
                "message": "Resume enhancement initiated successfully.",
                "task_id": task_record.task_id,
                "status_url": f"/api/resume/enhancement-status/{task_record.task_id}/",
            },
            status=202,
        )

    except Exception as e:
        return Response({"error": f"Failed to initiate resume enhancement: {str(e)}"}, status=500)


from rest_framework.generics import ListAPIView


class SkillListPagination(PageNumberPagination):
    """
    Custom pagination for SkillListView to prevent memory issues.
    """

    page_size = 100
    page_size_query_param = "page_size"
    max_page_size = 500


class SkillListView(ListAPIView):
    """
    Read-only endpoint to fetch all available skills (for dropdowns).
    Optimized with pagination and prefetch_related to prevent memory issues.
    Returns skills in alphabetical order.
    """

    queryset = Skill.objects.prefetch_related("categories").order_by("name")
    serializer_class = SkillListSerializer
    permission_classes = [AllowAny]
    pagination_class = SkillListPagination

    def get_queryset(self):
        """
        Override to add search functionality and optimize queries.
        Returns skills in alphabetical order.
        """
        queryset = Skill.objects.prefetch_related("categories").order_by("name")
        search = self.request.query_params.get("search", None)
        if search:
            queryset = queryset.filter(name__icontains=search)
        return queryset


@api_view(["PATCH", "PUT"])
def update_resume_fields_api(request):
    """
    Update specific fields of the authenticated user's Resume.
    Accepts PATCH or PUT with any subset of the Resume fields.
    """
    user = request.user
    try:
        resume = Resume.objects.get(user=user)
    except Resume.DoesNotExist:
        return Response({"error": "Resume not found for this user."}, status=404)

    # Use the serializer for validation and partial update
    serializer = ResumeSerializer(resume, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=200)
    else:
        return Response(serializer.errors, status=400)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def enhancement_history_api(request):
    """
    Retrieves all enhanced resumes for the authenticated user.

    Response:
        [
            {
                "id": 1,
                "user": 1,
                "job": 2,
                "full_name": "...",
                ...
            },
            ...
        ]
    """
    enhanced_resumes = EnhancedResume.objects.filter(user=request.user).order_by("-created_at")
    serializer = EnhancedResumeSerializer(enhanced_resumes, many=True)
    return Response(serializer.data, status=200)


@api_view(["GET"])
def check_enhanced_resume_api(request, user_id, job_id):
    """
    Checks if a user has enhanced a resume for a particular job.

    URL Parameters:
        user_id: ID of the user
        job_id: ID of the job

    Response:
        {
            "has_enhanced": true/false,
            "enhanced_resume": {...}  # Only if exists
        }
    """
    enhanced_resume = EnhancedResume.objects.filter(user_id=user_id, job_id=job_id).first()
    if enhanced_resume:
        serializer = EnhancedResumeSerializer(enhanced_resume)
        return Response({"has_enhanced": True, "enhanced_resume": serializer.data}, status=200)
    else:
        return Response({"has_enhanced": False}, status=200)


from rest_framework.generics import ListAPIView


@api_view(["GET"])
def resume_enhancement_status(request, task_id):
    """
    Check the status of a resume enhancement task.

    URL Parameter:
        task_id: The ID of the task to check.

    Response:
        {
            "status": "pending|processing|completed|failed",
            "message": "Status message",
            "enhanced_resume": {...},  // Only if completed
            "error_message": "Error details"  // Only if failed
        }
    """
    try:
        from .models import ResumeEnhancementTask

        task_record = ResumeEnhancementTask.objects.get(task_id=task_id, user=request.user)

        response_data = {
            "status": task_record.status,
            "task_id": task_record.task_id,
            "created_at": task_record.created_at,
            "updated_at": task_record.updated_at,
        }

        if task_record.status == "completed" and task_record.enhanced_resume:
            # Include the enhanced resume data
            enhanced_resume = task_record.enhanced_resume
            response_data["enhanced_resume"] = {
                "id": enhanced_resume.id,
                "full_name": enhanced_resume.full_name,
                "email": enhanced_resume.email,
                "phone": enhanced_resume.phone,
                "linkedin": enhanced_resume.linkedin,
                "location": enhanced_resume.location,
                "summary": enhanced_resume.summary,
                "skills": enhanced_resume.skills,
                "experience": enhanced_resume.experience,
                "education": enhanced_resume.education,
                "created_at": enhanced_resume.created_at,
            }
            response_data["message"] = "Resume enhancement completed successfully."

        elif task_record.status == "failed":
            response_data["error_message"] = (
                task_record.error_message or "An unknown error occurred."
            )
            response_data["message"] = "Resume enhancement failed."

        elif task_record.status == "processing":
            response_data["message"] = "Resume enhancement is in progress."

        else:  # pending
            response_data["message"] = "Resume enhancement is queued for processing."

        return Response(response_data, status=200)

    except ResumeEnhancementTask.DoesNotExist:
        return Response(
            {"error": "Task not found or you don't have permission to access it."}, status=404
        )
    except Exception as e:
        return Response({"error": f"Failed to check task status: {str(e)}"}, status=500)


# New endpoints for frontend
from rest_framework.views import APIView


class CountriesAPIView(APIView):
    """
    Get list of all countries for dropdown selections.
    
    **Response:**
    ```json
    {
        "countries": [
            {
                "code": "US",
                "name": "United States"
            },
            {
                "code": "CA", 
                "name": "Canada"
            }
        ]
    }
    ```
    """
    permission_classes = []  # No authentication required for countries list
    
    def get(self, request):
        """Get list of all countries"""
        try:
            serializer = CountriesSerializer(None)
            return Response(serializer.to_representation(None), status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Failed to retrieve countries: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class StatesAPIView(APIView):
    """
    Get list of US states for dropdown selections with "Not in US" option at top.
    
    **Response:**
    ```json
    {
        "states": [
            {
                "code": "NOT_US",
                "name": "Not in US"
            },
            {
                "code": "NY",
                "name": "New York"
            },
            {
                "code": "CA", 
                "name": "California"
            }
        ]
    }
    ```
    """
    permission_classes = []  # No authentication required for states list
    
    def get(self, request):
        """Get list of US states with 'Not in US' option at top"""
        try:
            us_states = [
                {"code": "NOT_US", "name": "Not in US"},  # Always at top for international users
                {"code": "AL", "name": "Alabama"},
                {"code": "AK", "name": "Alaska"},
                {"code": "AZ", "name": "Arizona"},
                {"code": "AR", "name": "Arkansas"},
                {"code": "CA", "name": "California"},
                {"code": "CO", "name": "Colorado"},
                {"code": "CT", "name": "Connecticut"},
                {"code": "DE", "name": "Delaware"},
                {"code": "FL", "name": "Florida"},
                {"code": "GA", "name": "Georgia"},
                {"code": "HI", "name": "Hawaii"},
                {"code": "ID", "name": "Idaho"},
                {"code": "IL", "name": "Illinois"},
                {"code": "IN", "name": "Indiana"},
                {"code": "IA", "name": "Iowa"},
                {"code": "KS", "name": "Kansas"},
                {"code": "KY", "name": "Kentucky"},
                {"code": "LA", "name": "Louisiana"},
                {"code": "ME", "name": "Maine"},
                {"code": "MD", "name": "Maryland"},
                {"code": "MA", "name": "Massachusetts"},
                {"code": "MI", "name": "Michigan"},
                {"code": "MN", "name": "Minnesota"},
                {"code": "MS", "name": "Mississippi"},
                {"code": "MO", "name": "Missouri"},
                {"code": "MT", "name": "Montana"},
                {"code": "NE", "name": "Nebraska"},
                {"code": "NV", "name": "Nevada"},
                {"code": "NH", "name": "New Hampshire"},
                {"code": "NJ", "name": "New Jersey"},
                {"code": "NM", "name": "New Mexico"},
                {"code": "NY", "name": "New York"},
                {"code": "NC", "name": "North Carolina"},
                {"code": "ND", "name": "North Dakota"},
                {"code": "OH", "name": "Ohio"},
                {"code": "OK", "name": "Oklahoma"},
                {"code": "OR", "name": "Oregon"},
                {"code": "PA", "name": "Pennsylvania"},
                {"code": "RI", "name": "Rhode Island"},
                {"code": "SC", "name": "South Carolina"},
                {"code": "SD", "name": "South Dakota"},
                {"code": "TN", "name": "Tennessee"},
                {"code": "TX", "name": "Texas"},
                {"code": "UT", "name": "Utah"},
                {"code": "VT", "name": "Vermont"},
                {"code": "VA", "name": "Virginia"},
                {"code": "WA", "name": "Washington"},
                {"code": "WV", "name": "West Virginia"},
                {"code": "WI", "name": "Wisconsin"},
                {"code": "WY", "name": "Wyoming"},
                {"code": "DC", "name": "District of Columbia"},
            ]
            return Response({"states": us_states}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Failed to retrieve states: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class AboutAPIView(APIView):
    """
    Manages user's about/bio information.
    
    **GET Response:**
    ```json
    {
        "about": {
            "firstName": "John",
            "lastName": "Doe", 
            "bio": "Experienced software engineer...",
            "description": "Passionate about creating..."
        }
    }
    ```
    
    **PUT/PATCH Request:** Same structure as GET response
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user's about information"""
        try:
            # Get or create resume for the user
            resume, created = Resume.objects.get_or_create(user=request.user)
            serializer = AboutSerializer(resume)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Failed to retrieve about information: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request):
        """Update user's about information (full update)"""
        return self._update_about(request, partial=False)
    
    def patch(self, request):
        """Update user's about information (partial update)"""
        return self._update_about(request, partial=True)
    
    def _update_about(self, request, partial=True):
        """Helper method to update about information"""
        try:
            # Get or create resume for the user
            resume, created = Resume.objects.get_or_create(user=request.user)
            
            # Extract data from request
            about_data = request.data.get('about', {})
            
            # Update user fields
            user = request.user
            if 'firstName' in about_data:
                user.first_name = about_data['firstName']
            if 'lastName' in about_data:
                user.last_name = about_data['lastName']
            user.save()
            
            # Update resume fields
            if 'bio' in about_data:
                resume.description = about_data['bio']
            elif 'description' in about_data:
                # Only use description if bio is not provided
                resume.description = about_data['description']
            resume.save()
            
            # Refresh the user object to get updated data
            user.refresh_from_db()
            resume.refresh_from_db()
            
            # Return updated data - pass both user and resume to ensure proper serialization
            serializer = AboutSerializer(resume)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to update about information: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PersonalDetailsAPIView(APIView):
    """
    Manages user's personal details and contact information.
    
    **GET Response:**
    ```json
    {
        "personalDetails": {
            "email": "john.doe@example.com",
            "dob": "25th Dec, 1990",
            "address": "123 Main Street",
            "city": "New York",
            "country": "United States",
            "postalCode": "10001",
            "mobile": "+1-234-567-8900",
            "jobTitle": "Software Engineer"
        }
    }
    ```
    
    **PUT/PATCH Request:** Same structure as GET response
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user's personal details"""
        try:
            # Get or create resume for the user
            resume, created = Resume.objects.get_or_create(user=request.user)
            serializer = PersonalDetailsSerializer(resume)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Failed to retrieve personal details: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def put(self, request):
        """Update user's personal details (full update)"""
        return self._update_personal_details(request, partial=False)
    
    def patch(self, request):
        """Update user's personal details (partial update)"""
        return self._update_personal_details(request, partial=True)
    
    def _update_personal_details(self, request, partial=True):
        """Helper method to update personal details"""
        try:
            # Get or create resume for the user
            resume, created = Resume.objects.get_or_create(user=request.user)
            
            # Extract data from request
            personal_data = request.data.get('personalDetails', {})
            
            # Update user fields
            user = request.user
            if 'email' in personal_data and personal_data['email']:
                # Validate email format
                from django.core.validators import validate_email
                from django.core.exceptions import ValidationError as DjangoValidationError
                try:
                    validate_email(personal_data['email'])
                    user.email = personal_data['email']
                except DjangoValidationError:
                    return Response(
                        {"error": "Invalid email format"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            user.save()
            
            # Update resume fields
            if 'dob' in personal_data and personal_data['dob']:
                # Parse date format like "31st Dec, 1996"
                from datetime import datetime
                try:
                    dob_str = personal_data['dob'].strip()
                    if dob_str:
                        # Remove ordinal suffixes and normalize
                        import re
                        dob_clean = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', dob_str)
                        # Try multiple date formats
                        for fmt in ['%d %b, %Y', '%d %B, %Y', '%d/%m/%Y', '%Y-%m-%d']:
                            try:
                                resume.date_of_birth = datetime.strptime(dob_clean, fmt).date()
                                break
                            except ValueError:
                                continue
                except Exception:
                    pass  # Keep existing date if parsing fails
            
            # Handle address field (can be used for street address)
            if 'address' in personal_data:
                # For now, we'll store address in a separate field if needed
                # You might want to add an address field to the Resume model
                pass
            
            # Handle city field
            if 'city' in personal_data:
                # Store city information - you might want to add a city field to Resume model
                # For now, we'll combine city and state if both are provided
                city = personal_data['city'] or ''
                if city and resume.state and resume.state != "NOT_US":
                    resume.state = f"{city}, {resume.state}"
                elif city:
                    resume.state = city
            
            # Handle state field - this is the main state field from dropdown
            if 'state' in personal_data:
                state_value = personal_data['state'] or ''
                if state_value == "NOT_US":
                    # User selected "Not in US" - clear state field
                    resume.state = ""
                else:
                    # User selected a US state - save the state name
                    resume.state = state_value
            
            if 'country' in personal_data:
                # Validate country code/name against django-countries
                from django_countries import countries
                country_input = personal_data['country']
                # Check if it's a valid country name or code
                valid_country = None
                for code, name in countries:
                    if country_input == name or country_input == code:
                        valid_country = name
                        break
                if valid_country:
                    resume.country = valid_country
                else:
                    resume.country = country_input  # Save as-is if not found
            if 'mobile' in personal_data:
                resume.phone = personal_data['mobile'] or ''
            if 'jobTitle' in personal_data:
                resume.job_title = personal_data['jobTitle'] or ''
            # Note: postalCode is not in current model, you might want to add it to Resume model
            
            resume.save()
            
            # Return updated data
            serializer = PersonalDetailsSerializer(resume)
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to update personal details: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserLocationAPIView(APIView):
    """
    Manages user's country and city information.
    
    **GET Response:**
    ```json
    {
        "location": {
            "country": "US",
            "country_name": "United States",
            "city": "New York"
        }
    }
    ```
    
    **POST/PATCH Request:**
    ```json
    {
        "country": "CA",
        "city": "Toronto"
    }
    ```
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user's current country and city"""
        try:
            # Try to get from ContactInfo first
            contact_info = ContactInfo.objects.filter(user=request.user).first()
            if contact_info:
                return Response({
                    "location": {
                        "country": contact_info.country.code,
                        "country_name": contact_info.country.name,
                        "city": contact_info.city or ""
                    }
                }, status=status.HTTP_200_OK)
            
            # Fallback to Resume model
            resume = Resume.objects.filter(user=request.user).first()
            if resume:
                return Response({
                    "location": {
                        "country": resume.country or "",
                        "country_name": resume.country or "",
                        "city": resume.state or ""  # Resume uses state field for city
                    }
                }, status=status.HTTP_200_OK)
            
            # Return empty if no data found
            return Response({
                "location": {
                    "country": "",
                    "country_name": "",
                    "city": ""
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to retrieve location: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Create or update user's country and city"""
        return self._update_location(request, partial=False)
    
    def patch(self, request):
        """Update user's country and city (partial update)"""
        return self._update_location(request, partial=True)
    
    def _update_location(self, request, partial=True):
        """Helper method to update location information"""
        try:
            location_data = request.data.get('location', request.data)
            country_code = location_data.get('country', '').strip()
            city = location_data.get('city', '').strip()
            
            # Validate country code
            if country_code:
                from django_countries import countries
                valid_countries = [code for code, name in countries]
                if country_code not in valid_countries:
                    return Response(
                        {"error": f"Invalid country code: {country_code}"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
            
            # Update ContactInfo (preferred)
            contact_info, created = ContactInfo.objects.get_or_create(
                user=request.user,
                defaults={
                    'name': f"{request.user.first_name or ''} {request.user.last_name or ''}".strip(),
                    'email': request.user.email,
                    'phone': '',
                    'country': country_code or 'US',
                    'city': city
                }
            )
            
            if not created:
                # Update existing ContactInfo
                if country_code:
                    contact_info.country = country_code
                if city:
                    contact_info.city = city
                contact_info.save()
            
            # Also update Resume model for consistency
            resume, created = Resume.objects.get_or_create(user=request.user)
            if country_code:
                resume.country = country_code
            if city:
                resume.state = city  # Resume uses state field for city
            resume.save()
            
            # Return updated location
            return Response({
                "location": {
                    "country": contact_info.country.code,
                    "country_name": contact_info.country.name,
                    "city": contact_info.city or ""
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to update location: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class UserImagesAPIView(APIView):
    """
    Manages user's profile and cover images.
    
    **GET Response:**
    ```json
    {
        "images": {
            "profile_image": "/media/resume/images/profile_123.jpg",
            "cover_image": "/media/resume/covers/cover_123.jpg"
        }
    }
    ```
    
    **POST Request (Upload Profile Image):**
    ```
    Content-Type: multipart/form-data
    profile_image: [file]
    ```
    
    **POST Request (Upload Cover Image):**
    ```
    Content-Type: multipart/form-data
    cover_image: [file]
    ```
    
    **DELETE Request:**
    ```
    DELETE /api/resume/user-images/?type=profile_image
    DELETE /api/resume/user-images/?type=cover_image
    ```
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def get(self, request):
        """Get user's current images"""
        try:
            # Get or create resume for the user
            resume, created = Resume.objects.get_or_create(user=request.user)
            
            return Response({
                "images": {
                    "profile_image": resume.profile_image.url if resume.profile_image else None,
                    "cover_image": resume.cover_image.url if resume.cover_image else None
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to retrieve images: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Upload profile or cover image"""
        try:
            # Get or create resume for the user
            resume, created = Resume.objects.get_or_create(user=request.user)
            
            # Check which image is being uploaded
            if 'profile_image' in request.FILES:
                image_file = request.FILES['profile_image']
                # Validate image file
                if not image_file.content_type.startswith('image/'):
                    return Response(
                        {"error": "File must be an image"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Save profile image
                resume.profile_image = image_file
                resume.save()
                
                return Response({
                    "message": "Profile image uploaded successfully",
                    "profile_image": resume.profile_image.url
                }, status=status.HTTP_200_OK)
                
            elif 'cover_image' in request.FILES:
                image_file = request.FILES['cover_image']
                # Validate image file
                if not image_file.content_type.startswith('image/'):
                    return Response(
                        {"error": "File must be an image"}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                # Save cover image
                resume.cover_image = image_file
                resume.save()
                
                return Response({
                    "message": "Cover image uploaded successfully",
                    "cover_image": resume.cover_image.url
                }, status=status.HTTP_200_OK)
                
            else:
                return Response(
                    {"error": "No image file provided. Use 'profile_image' or 'cover_image' field."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {"error": f"Failed to upload image: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request):
        """Delete profile or cover image"""
        try:
            # Get resume for the user
            resume = Resume.objects.filter(user=request.user).first()
            if not resume:
                return Response(
                    {"error": "No resume found for user"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Check which image to delete
            image_type = request.query_params.get('type', '').lower()
            
            if image_type == 'profile_image':
                if resume.profile_image:
                    # Delete the file from storage
                    resume.profile_image.delete(save=False)
                    resume.profile_image = None
                    resume.save()
                    return Response(
                        {"message": "Profile image deleted successfully"}, 
                        status=status.HTTP_200_OK
                    )
                else:
                    return Response(
                        {"error": "No profile image to delete"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
                    
            elif image_type == 'cover_image':
                if resume.cover_image:
                    # Delete the file from storage
                    resume.cover_image.delete(save=False)
                    resume.cover_image = None
                    resume.save()
                    return Response(
                        {"message": "Cover image deleted successfully"}, 
                        status=status.HTTP_200_OK
                    )
                else:
                    return Response(
                        {"error": "No cover image to delete"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
                    
            else:
                return Response(
                    {"error": "Invalid image type. Use 'profile_image' or 'cover_image'."}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            return Response(
                {"error": f"Failed to delete image: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExperiencesAPIView(APIView):
    """
    Manages user's work experiences.
    
    **GET Response:**
    ```json
    {
        "experiences": [
            {
                "id": 1,
                "period": "2019-22",
                "logo": "/assets/shree-logo-Bd9DHJ8p.png",
                "title": "Full Stack Developer",
                "company": "Shreethemes - India",
                "description": "Detailed job description..."
            }
        ]
    }
    ```
    
    **POST Request:**
    ```json
    {
        "title": "Software Engineer",      // Required
        "company": "Tech Corp",           // Required  
        "period": "2020-22",             // Optional - Format: "YYYY-YY"
        "description": "Job duties..."    // Optional
    }
    ```
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user's experiences list"""
        try:
            # Get or create resume for the user to ensure consistency
            resume, created = Resume.objects.get_or_create(user=request.user)
            serializer = ExperienceListSerializer(resume)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Failed to retrieve experiences: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Create a new experience"""
        try:
            experience_data = request.data
            
            # Parse period if provided (e.g., "2019-22" or "2019-Present")
            start_date = None
            end_date = None
            if 'period' in experience_data:
                period = experience_data['period']
                try:
                    if '-' in period:
                        start_str, end_str = period.split('-')
                        start_year = int(start_str)
                        
                        if end_str.lower() != 'present':
                            # Handle short year format like "22" -> 2022
                            if len(end_str) == 2:
                                end_year = 2000 + int(end_str)
                            else:
                                end_year = int(end_str)
                            end_date = f"{end_year}-12-31"  # Default to end of year
                        
                        start_date = f"{start_year}-01-01"  # Default to start of year
                except:
                    pass  # Keep dates as None if parsing fails
            
            # Create experience
            experience = Experience.objects.create(
                user=request.user,
                company_name=experience_data.get('company', ''),
                role=experience_data.get('title', ''),
                start_date=start_date,
                end_date=end_date
            )
            
            # Return updated experiences list
            resume, created = Resume.objects.get_or_create(user=request.user)
            serializer = ExperienceListSerializer(resume)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to create experience: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EducationAPIView(APIView):
    """
    Manages user's education records.
    
    **GET Response:**
    ```json
    {
        "education": [
            {
                "id": 1,
                "period": "2013-17",
                "degree": "Bachelor of Computer Science",
                "university": "University of London",
                "description": "Specialized in web development..."
            }
        ]
    }
    ```
    
    **POST Request:**
    ```json
    {
        "degree": "Master of Science",        // Required
        "university": "Stanford University",  // Required
        "period": "2020-22",                 // Optional - Format: "YYYY-YY"
        "description": "Specialized in ML..."  // Optional
    }
    ```
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user's education list"""
        try:
            # Get or create resume for the user to ensure consistency
            resume, created = Resume.objects.get_or_create(user=request.user)
            serializer = EducationListSerializer(resume)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"Failed to retrieve education: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Create a new education record"""
        try:
            education_data = request.data
            
            # Parse period if provided (e.g., "2013-17")
            graduation_year = None
            if 'period' in education_data:
                period = education_data['period']
                try:
                    if '-' in period:
                        start_str, end_str = period.split('-')
                        # Handle short year format like "17" -> 2017
                        if len(end_str) == 2:
                            graduation_year = 2000 + int(end_str)
                        else:
                            graduation_year = int(end_str)
                except:
                    pass  # Keep graduation_year as None if parsing fails
            
            # Create education
            education = Education.objects.create(
                user=request.user,
                institution_name=education_data.get('university', ''),
                degree=education_data.get('degree', ''),
                field_of_study=education_data.get('description', ''),
                graduation_year=graduation_year or 2023  # Default year if not provided
            )
            
            # Return updated education list
            resume, created = Resume.objects.get_or_create(user=request.user)
            serializer = EducationListSerializer(resume)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to create education record: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SkillsPagination(PageNumberPagination):
    """
    Custom pagination for SkillsAPIView.
    """
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class SkillsAPIView(APIView):
    """
    Manages user's skills with pagination, search, and job title filtering.
    
    **Key Point:** POST/DELETE expect skill IDs, GET returns both id and name.
    
    **GET Response:**
    ```json
    {
        "count": 50,
        "results": {
            "skills": [
                {
                    "id": 1,
                    "name": "JavaScript",
                    "is_user_skill": true,
                    "categories": ["Frontend Development"]
                }
            ],
            "filter_applied": "job_relevant"
        }
    }
    ```
    
    **POST Request (Add Skills):**
    ```json
    {
        "skill_id": 15    // Single skill
    }
    // OR
    {
        "skill_ids": [15, 23, 45]    // Multiple skills
    }
    ```
    
    **DELETE Request (Remove Skills):**
    ```json
    {
        "skill_id": 15    // Single skill
    }
    // OR
    {
        "skill_ids": [15, 23, 45]    // Multiple skills
    }
    ```
    
    **Query Parameters:**
    - `page`: Page number (default: 1)
    - `page_size`: Items per page (default: 20, max: 100)
    - `search`: Search skills by name
    - `filter`: 'job_relevant' (default), 'user_only', or 'all'
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get user's skills list with pagination, search, and optional job title filtering"""
        try:
            # Start with user's existing skills
            user_skills = Skill.objects.filter(user=request.user)
            
            # Get filter type - 'user_only', 'job_relevant', or 'all' (default: 'job_relevant')
            filter_type = request.query_params.get('filter', 'job_relevant')
            
            if filter_type == 'job_relevant':
                # Get user's job title category ID from Resume or ContactInfo
                user_job_category_id = None
                
                # First try to get from ContactInfo (more structured)
                contact_info = ContactInfo.objects.filter(user=request.user).first()
                if contact_info and contact_info.job_title_id:
                    user_job_category_id = contact_info.job_title_id
                else:
                    # Fallback: try to match Resume job_title with SkillCategory
                    resume = Resume.objects.filter(user=request.user).first()
                    if resume and resume.job_title:
                        job_category = SkillCategory.objects.filter(
                            name__icontains=resume.job_title
                        ).first()
                        if job_category:
                            user_job_category_id = job_category.id
                
                if user_job_category_id:
                    # Get relevant skills from the same category using category ID
                    relevant_skills = Skill.objects.filter(
                        categories__id=user_job_category_id
                    )
                    
                    # Combine user skills with relevant skills from job category using Q objects
                    from django.db.models import Q
                    skills = Skill.objects.filter(
                        Q(user=request.user) | Q(categories__id=user_job_category_id)
                    ).distinct()
                else:
                    # If no job title found, just show user's skills
                    skills = user_skills
                    
            elif filter_type == 'user_only':
                # Show only user's existing skills
                skills = user_skills
            else:  # 'all'
                # Show all available skills
                skills = Skill.objects.all()
            
            # Apply search filter if provided
            search = request.query_params.get('search', None)
            if search:
                skills = skills.filter(name__icontains=search)
            
            # Order by name
            skills = skills.order_by('name')
            
            # Apply pagination
            paginator = SkillsPagination()
            paginated_skills = paginator.paginate_queryset(skills, request)
            
            # Serialize the paginated data with ownership indication
            skills_data = []
            user_skill_ids = set(user_skills.values_list('id', flat=True))
            
            for skill in paginated_skills:
                skills_data.append({
                    "id": skill.id,
                    "name": skill.name,
                    "is_user_skill": skill.id in user_skill_ids,  # Indicate if user already has this skill
                    "categories": [cat.name for cat in skill.categories.all()]  # Show categories
                })
            
            # Return paginated response
            job_category_name = None
            if 'user_job_category_id' in locals() and user_job_category_id:
                try:
                    job_category = SkillCategory.objects.get(id=user_job_category_id)
                    job_category_name = job_category.name
                except SkillCategory.DoesNotExist:
                    pass
            
            return paginator.get_paginated_response({
                "skills": skills_data,
                "filter_applied": filter_type,
                "job_category": job_category_name
            })
            
        except Exception as e:
            return Response(
                {"error": f"Failed to retrieve skills: {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def post(self, request):
        """Add existing skill(s) to user's profile using skill ID(s) (ManyToMany)"""
        try:
            skill_data = request.data
            
            # Support both single skill_id and multiple skill_ids
            skill_id = skill_data.get('skill_id')
            skill_ids = skill_data.get('skill_ids', [])
            
            # Determine which format is being used
            if skill_id is not None:
                # Single skill format: {"skill_id": 15}
                skill_ids_to_process = [skill_id]
            elif skill_ids:
                # Multiple skills format: {"skill_ids": [15, 23, 45]}
                skill_ids_to_process = skill_ids
            else:
                return Response(
                    {"error": "Either 'skill_id' or 'skill_ids' is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Validate skill IDs exist
            skills_to_add = []
            for sid in skill_ids_to_process:
                try:
                    skill = Skill.objects.get(id=sid)
                    skills_to_add.append(skill)
                except Skill.DoesNotExist:
                    return Response(
                        {"error": f"Skill with ID {sid} not found"}, 
                        status=status.HTTP_404_NOT_FOUND
                    )
            
            # Get or create the user's resume
            resume, _ = Resume.objects.get_or_create(user=request.user)
            
            # Check for duplicates and collect skills to actually add
            skills_added = []
            skills_already_owned = []
            
            for skill in skills_to_add:
                if resume.skills.filter(id=skill.id).exists():
                    skills_already_owned.append(skill.name)
                else:
                    resume.skills.add(skill)
                    skills_added.append(skill.name)
            
            # Prepare response message
            response_data = {
                "message": f"Successfully added {len(skills_added)} skill(s)",
                "skills_added": skills_added,
            }
            
            if skills_already_owned:
                response_data["skills_already_owned"] = skills_already_owned
                response_data["message"] += f", {len(skills_already_owned)} already owned"

            # Return updated skills list following the same filtering as GET
            filter_type = request.query_params.get('filter', 'job_relevant')
            user_skills = resume.skills.all()
            if filter_type == 'job_relevant':
                user_job_category_id = None
                # First try to get from ContactInfo (more structured)
                contact_info = ContactInfo.objects.filter(user=request.user).first()
                if contact_info and contact_info.job_title_id:
                    user_job_category_id = contact_info.job_title_id
                else:
                    # Fallback: try to match Resume job_title with SkillCategory
                    resume = Resume.objects.filter(user=request.user).first()
                    if resume and resume.job_title:
                        job_category = SkillCategory.objects.filter(
                            name__icontains=resume.job_title
                        ).first()
                        if job_category:
                            user_job_category_id = job_category.id
                
                if user_job_category_id:
                    # Get relevant skills from the same category using category ID
                    from django.db.models import Q
                    skills = Skill.objects.filter(
                        Q(user=request.user) | Q(categories__id=user_job_category_id)
                    ).distinct()
                else:
                    # If no job title found, just show user's skills
                    skills = user_skills
                    
            elif filter_type == 'user_only':
                # Show only user's existing skills
                skills = user_skills
            else:  # 'all'
                # Show all available skills
                skills = Skill.objects.all()
            
            # Apply search filter if provided
            search = request.query_params.get('search', None)
            if search:
                skills = skills.filter(name__icontains=search)
                
            # Order and apply pagination
            skills = skills.order_by('name')
            paginator = SkillsPagination()
            paginated_skills = paginator.paginate_queryset(skills, request)
            
            # Serialize with ownership indication
            skills_data = []
            user_skill_ids = set(user_skills.values_list('id', flat=True))
            
            for skill in paginated_skills:
                skills_data.append({
                    "id": skill.id,
                    "name": skill.name,
                    "is_user_skill": skill.id in user_skill_ids,
                    "categories": [cat.name for cat in skill.categories.all()]
                })
            
            # Return paginated response with added skills info
            job_category_name = None
            if 'user_job_category_id' in locals() and user_job_category_id:
                try:
                    job_category = SkillCategory.objects.get(id=user_job_category_id)
                    job_category_name = job_category.name
                except SkillCategory.DoesNotExist:
                    pass
            
            paginated_response = paginator.get_paginated_response({
                "skills": skills_data,
                "filter_applied": filter_type,
                "job_category": job_category_name
            })
            
            # Add skills operation results to response
            response_data["results"] = paginated_response.data["results"]
            response_data["count"] = paginated_response.data["count"]
            response_data["next"] = paginated_response.data["next"]
            response_data["previous"] = paginated_response.data["previous"]
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to add skill(s): {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request):
        """Remove skill(s) from user's profile using skill ID(s)"""
        try:
            skill_data = request.data
            
            # Support both single skill_id and multiple skill_ids
            skill_id = skill_data.get('skill_id')
            skill_ids = skill_data.get('skill_ids', [])
            
            # Determine which format is being used
            if skill_id is not None:
                # Single skill format: {"skill_id": 15}
                skill_ids_to_process = [skill_id]
            elif skill_ids:
                # Multiple skills format: {"skill_ids": [15, 23, 45]}
                skill_ids_to_process = skill_ids
            else:
                return Response(
                    {"error": "Either 'skill_id' or 'skill_ids' is required"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get user's resume
            try:
                resume = Resume.objects.get(user=request.user)
            except Resume.DoesNotExist:
                return Response(
                    {"error": "No resume found for user"}, 
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Validate skill IDs and collect skills to remove
            skills_to_remove = []
            skills_not_found = []
            skills_not_owned = []
            
            for sid in skill_ids_to_process:
                try:
                    skill = Skill.objects.get(id=sid)
                    if resume.skills.filter(id=skill.id).exists():
                        skills_to_remove.append(skill)
                    else:
                        skills_not_owned.append(skill.name)
                except Skill.DoesNotExist:
                    skills_not_found.append(sid)
            
            # Remove skills from user's profile
            skills_removed = []
            for skill in skills_to_remove:
                resume.skills.remove(skill)
                skills_removed.append(skill.name)
            
            # Prepare response message
            response_data = {
                "message": f"Successfully removed {len(skills_removed)} skill(s)",
                "skills_removed": skills_removed,
            }
            
            if skills_not_owned:
                response_data["skills_not_owned"] = skills_not_owned
                response_data["message"] += f", {len(skills_not_owned)} not owned"
                
            if skills_not_found:
                response_data["skills_not_found"] = skills_not_found
                response_data["message"] += f", {len(skills_not_found)} not found"
            
            # Return updated skills list (same logic as GET/POST)
            filter_type = request.query_params.get('filter', 'job_relevant')
            user_skills = resume.skills.all()
            
            if filter_type == 'job_relevant':
                user_job_category_id = None
                contact_info = ContactInfo.objects.filter(user=request.user).first()
                if contact_info and contact_info.job_title_id:
                    user_job_category_id = contact_info.job_title_id
                else:
                    resume_obj = Resume.objects.filter(user=request.user).first()
                    if resume_obj and resume_obj.job_title:
                        job_category = SkillCategory.objects.filter(
                            name__icontains=resume_obj.job_title
                        ).first()
                        if job_category:
                            user_job_category_id = job_category.id
                
                if user_job_category_id:
                    from django.db.models import Q
                    skills = Skill.objects.filter(
                        Q(user=request.user) | Q(categories__id=user_job_category_id)
                    ).distinct()
                else:
                    skills = user_skills
                    
            elif filter_type == 'user_only':
                skills = user_skills
            else:  # 'all'
                skills = Skill.objects.all()
            
            # Apply search filter if provided
            search = request.query_params.get('search', None)
            if search:
                skills = skills.filter(name__icontains=search)
                
            # Order and apply pagination
            skills = skills.order_by('name')
            paginator = SkillsPagination()
            paginated_skills = paginator.paginate_queryset(skills, request)
            
            # Serialize with ownership indication
            skills_data = []
            user_skill_ids = set(user_skills.values_list('id', flat=True))
            
            for skill in paginated_skills:
                skills_data.append({
                    "id": skill.id,
                    "name": skill.name,
                    "is_user_skill": skill.id in user_skill_ids,
                    "categories": [cat.name for cat in skill.categories.all()]
                })
            
            # Return paginated response with removed skills info
            job_category_name = None
            if 'user_job_category_id' in locals() and user_job_category_id:
                try:
                    job_category = SkillCategory.objects.get(id=user_job_category_id)
                    job_category_name = job_category.name
                except SkillCategory.DoesNotExist:
                    pass
            
            paginated_response = paginator.get_paginated_response({
                "skills": skills_data,
                "filter_applied": filter_type,
                "job_category": job_category_name
            })
            
            # Add skills operation results to response
            response_data["results"] = paginated_response.data["results"]
            response_data["count"] = paginated_response.data["count"]
            response_data["next"] = paginated_response.data["next"]
            response_data["previous"] = paginated_response.data["previous"]
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response(
                {"error": f"Failed to remove skill(s): {str(e)}"}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
