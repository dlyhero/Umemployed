import os  # Add this import for accessing environment variables
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView
from resume.models import (
    Skill, Education, Experience, ContactInfo, WorkExperience, Language, ResumeAnalysis, ProfileView
)
from .serializers import (
    SkillSerializer, EducationSerializer, ExperienceSerializer, ContactInfoSerializer, 
    WorkExperienceSerializer, LanguageSerializer, ResumeAnalysisSerializer, ProfileViewSerializer
)
from resume.models import Resume, ResumeDoc, Transcript
from resume.views import update_resume, resume_details, display_matching_jobs, upload_resume, update_resume_view
from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from resume.extract_pdf import extract_text  # Import the correct function
from resume.transcript_job_title import extract_transcript_text  # Import the old function
from azure.storage.blob import BlobServiceClient

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
def resume_details_api(request, pk):
    """
    Retrieves details of a specific resume by its primary key.

    This endpoint references the existing `resume_details` function in the `resume` app.

    Path Parameter:
        pk (int): The primary key of the resume.

    Response:
        {
            "id": 1,
            "user": 1,
            "first_name": "John",
            "surname": "Doe",
            ...
        }
    """
    return resume_details(request, pk)

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
            "extracted_text": "Extracted text from the resume."
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

    # Perform text extraction using the existing extract_text function
    try:
        file_path = resume_doc.file.name  # Use the file name as the file_path
        extract_text(request, file_path)  # Call the correct extract_text function
        resume_doc.refresh_from_db()  # Refresh the model to get updated extracted_text
        return Response({
            "message": "Resume uploaded and processed successfully.",
            "extracted_text": resume_doc.extracted_text
        }, status=200)
    except Exception as e:
        return Response({"error": f"Failed to extract text: {str(e)}"}, status=500)

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

@api_view(['GET'])
def skills_api(request):
    """
    Retrieves all skills.

    Response:
        [
            {
                "id": 1,
                "name": "Python",
                "categories": [1, 2],
                ...
            }
        ]
    """
    skills = Skill.objects.all()
    serializer = SkillSerializer(skills, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def educations_api(request):
    """
    Retrieves all education records.

    Response:
        [
            {
                "id": 1,
                "institution_name": "University of XYZ",
                "degree": "Bachelor's",
                ...
            }
        ]
    """
    educations = Education.objects.all()
    serializer = EducationSerializer(educations, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def experiences_api(request):
    """
    Retrieves all work experiences.

    Response:
        [
            {
                "id": 1,
                "company_name": "TechCorp",
                "role": "Software Engineer",
                ...
            }
        ]
    """
    experiences = Experience.objects.all()
    serializer = ExperienceSerializer(experiences, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def contact_info_api(request):
    """
    Retrieves all contact information.

    Response:
        [
            {
                "id": 1,
                "name": "John Doe",
                "email": "john.doe@example.com",
                ...
            }
        ]
    """
    contact_info = ContactInfo.objects.all()
    serializer = ContactInfoSerializer(contact_info, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def work_experiences_api(request):
    """
    Retrieves all work experiences.

    Response:
        [
            {
                "id": 1,
                "company_name": "TechCorp",
                "role": "Backend Developer",
                ...
            }
        ]
    """
    work_experiences = WorkExperience.objects.all()
    serializer = WorkExperienceSerializer(work_experiences, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def languages_api(request):
    """
    Retrieves all languages.

    Response:
        [
            {
                "id": 1,
                "name": "English"
            }
        ]
    """
    languages = Language.objects.all()
    serializer = LanguageSerializer(languages, many=True)
    return Response(serializer.data)

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
