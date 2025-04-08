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

@api_view(['POST'])
def update_resume_api(request):
    """
    Updates the resume for the authenticated user.

    This endpoint references the existing `update_resume` function in the `resume` app.
    It accepts a POST request with the necessary data to update the user's resume.

    Request Body:
        {
            "field_name": "value"
        }

    Response:
        {
            "message": "Resume updated successfully."
        }
    """
    return update_resume(request)

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

@api_view(['POST'])
def upload_transcript_api(request):
    """
    Handles transcript upload for the authenticated user.

    Request Body (Form-Data):
        file: Transcript file.

    Response:
        {
            "message": "Transcript uploaded successfully."
        }
    """
    transcript = Transcript(user=request.user, file=request.FILES['file'])
    transcript.save()
    return Response({"message": "Transcript uploaded successfully."})

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
