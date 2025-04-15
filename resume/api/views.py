import os  # Add this import for accessing environment variables
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from rest_framework.viewsets import ModelViewSet
from resume.models import (
    Skill, Education, Experience, ContactInfo, WorkExperience, Language, ResumeAnalysis, ProfileView, SkillCategory
)
from .serializers import (
    SkillSerializer, EducationSerializer, ExperienceSerializer, ContactInfoSerializer, 
    WorkExperienceSerializer, LanguageSerializer, ResumeAnalysisSerializer, ProfileViewSerializer, ResumeSerializer, SkillCategorySerializer
)
from resume.models import Resume, ResumeDoc, Transcript
from resume.views import update_resume, display_matching_jobs, upload_resume, update_resume_view
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from resume.extract_pdf import extract_text, extract_resume_details, parse_and_save_details, extract_technical_skills  # Import existing functions
from resume.transcript_job_title import extract_transcript_text  # Import the old function
from azure.storage.blob import BlobServiceClient
from django.db.models import Max  # Import Max for querying the latest resume
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
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
            return Response({"message": "Resume updated successfully."}, status=200)
        else:
            return Response({"error": "Failed to update resume."}, status=500)
    except Exception as e:
        return Response({"error": f"An error occurred: {str(e)}"}, status=500)

@api_view(['GET'])
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
        resume = Resume.objects.filter(user=user).order_by('-created_at').first()
        if not resume:
            return Response({"error": "No resume found for the current user."}, status=404)

        # Serialize the resume object
        serializer = ResumeSerializer(resume)
        return Response(serializer.data, status=200)
    except Exception as e:
        return Response({"error": f"An error occurred: {str(e)}"}, status=500)

@api_view(['GET'])
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

@api_view(['POST'])
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
    if 'file' not in request.FILES:
        return Response({"error": "The 'file' field is required."}, status=400)

    file = request.FILES['file']
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
            return Response({"error": "Failed to extract meaningful text from the resume."}, status=400)

        logger.info("Extracted text received in API: %s", extracted_text[:500])

        # Step 2: Extract and save details using extract_resume_details and parse_and_save_details
        extracted_details = extract_resume_details(request, extracted_text)
        parse_and_save_details(extracted_details, user)

        # Step 3: Extract technical skills and associate them with the ResumeDoc
        job_title = resume.job_title if resume.job_title else "Others"
        technical_skills = extract_technical_skills(request, extracted_text, job_title)

        # Save the extracted text and skills to the ResumeDoc
        resume_doc.extracted_text = extracted_text
        resume_doc.save()

        return Response({
            "message": "Resume uploaded and processed successfully.",
            "extracted_text": extracted_text,
            "technical_skills": technical_skills,
            "extracted_details": extracted_details
        }, status=200)
    except Exception as e:
        logger.error("Error in upload_resume_api: %s", e)
        return Response({"error": f"Failed to process resume: {str(e)}"}, status=500)

@api_view(['POST'])
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

@api_view(['POST'])
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
    if 'file' not in request.FILES:
        return Response({"error": "The 'file' field is required."}, status=400)

    file = request.FILES['file']
    user = request.user

    # Save the file to the Transcript model
    transcript = Transcript(user=user, file=file)
    try:
        transcript.save()
        print(f"Transcript uploaded: {transcript.file.name}")

        # Upload the file to Azure Blob Storage
        account_name = os.getenv('AZURE_ACCOUNT_NAME')
        account_key = os.getenv('AZURE_ACCOUNT_KEY')
        container_name = os.getenv('AZURE_CONTAINER')

        connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
        blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=transcript.file.name)

        # Upload the file
        with file.open('rb') as data:
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
        return Response({
            "message": "Transcript uploaded and processed successfully.",
            "extracted_text": transcript.extracted_text,
            "job_title": transcript.job_title,
            "reasoning": transcript.reasoning
        }, status=200)
    except Exception as e:
        return Response({"error": f"Failed to process transcript: {str(e)}"}, status=500)

@api_view(['POST'])
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
    transcript_id = request.data.get('transcript_id')
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
        # Ensure only skills associated with the logged-in user are fetched
        return Skill.objects.filter(user=self.request.user)

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
        return Education.objects.filter(user=self.request.user)

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
        return WorkExperience.objects.filter(user=self.request.user)

class LanguageViewSet(ModelViewSet):
    """
    Handles CRUD operations for user languages.
    - GET: Retrieve all languages for the logged-in user.
    - POST: Add a new language for the logged-in user.
    - PUT/PATCH: Update an existing language for the logged-in user.
    - DELETE: Delete a language for the logged-in user.
    """
    serializer_class = LanguageSerializer

    def get_queryset(self):
        # Filter languages through UserLanguage for the logged-in user
        return Language.objects.filter(userlanguage__user_profile__user=self.request.user)

@api_view(['GET'])
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

@api_view(['GET'])
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

@api_view(['POST'])
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
    if 'file' not in request.FILES:
        return Response({"error": "The 'file' field is required."}, status=400)

    file = request.FILES['file']
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
            overall_score=analysis_results['overall_score'],
            criteria_scores=analysis_results['criteria_scores'],
            improvement_suggestions=analysis_results['improvement_suggestions']
        )

        # Return the analysis results
        return Response({
            "overall_score": analysis_results['overall_score'],
            "criteria_scores": analysis_results['criteria_scores'],
            "improvement_suggestions": analysis_results['improvement_suggestions']
        }, status=200)
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
        skill_categories = SkillCategory.objects.all().order_by('name')  # Sort alphabetically
        serializer = SkillCategorySerializer(skill_categories, many=True)
        return Response(serializer.data)
