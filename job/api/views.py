from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from ..models import Job, Application, SavedJob, SkillCategory
from resume.models import Skill
from ..tasks import generate_questions_task
from ..job_description_algorithm import extract_technical_skills
from .serializers import JobSerializer, ApplicationSerializer, SavedJobSerializer
from ..generate_skills import generate_questions_task
from django_countries import countries  # Import the correct iterable for countries

class JobListAPIView(ListAPIView):
    queryset = Job.objects.filter(is_available=True)
    serializer_class = JobSerializer

class JobDetailAPIView(RetrieveAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer

class ApplyJobAPIView(APIView):
    def post(self, request, job_id):
        # ...logic to apply for a job...
        return Response({"message": "Job application submitted successfully."}, status=status.HTTP_201_CREATED)

class SaveJobAPIView(APIView):
    def post(self, request, job_id):
        # ...logic to save a job...
        return Response({"message": "Job saved successfully."}, status=status.HTTP_201_CREATED)

class WithdrawApplicationAPIView(APIView):
    def delete(self, request, job_id):
        # ...logic to withdraw a job application...
        return Response({"message": "Application withdrawn successfully."}, status=status.HTTP_200_OK)

class ShortlistCandidateAPIView(APIView):
    def post(self, request, job_id, candidate_id):
        # ...logic to shortlist a candidate...
        return Response({"message": "Candidate shortlisted successfully."}, status=status.HTTP_201_CREATED)

class DeclineCandidateAPIView(APIView):
    def post(self, request, job_id, candidate_id):
        # ...logic to decline a candidate...
        return Response({"message": "Candidate declined successfully."}, status=status.HTTP_201_CREATED)

class SavedJobsListAPIView(ListAPIView):
    serializer_class = SavedJobSerializer

    def get_queryset(self):
        return SavedJob.objects.filter(user=self.request.user)

class GenerateQuestionsAPIView(APIView):
    def post(self, request):
        job_title = request.data.get('job_title')
        entry_level = request.data.get('entry_level')
        skill_name = request.data.get('skill_name')
        questions_per_skill = request.data.get('questions_per_skill', 5)

        generate_questions_task.delay(job_title, entry_level, skill_name, questions_per_skill)
        return Response({"message": "Question generation started."}, status=status.HTTP_202_ACCEPTED)

class ExtractTechnicalSkillsAPIView(APIView):
    def post(self, request):
        job_title = request.data.get('job_title')
        job_description = request.data.get('job_description')

        if not job_title or not job_description:
            return Response({"error": "Job title and description are required."}, status=status.HTTP_400_BAD_REQUEST)

        skills = extract_technical_skills(job_title, job_description)
        return Response({"skills": skills}, status=status.HTTP_200_OK)

class AppliedJobsListAPIView(ListAPIView):
    serializer_class = ApplicationSerializer

    def get_queryset(self):
        return Application.objects.filter(user=self.request.user)


class CreateJobStep1APIView(APIView):
    """
    Endpoint to create the first step of a job.

    This step includes:
    - Title
    - Hire number
    - Job location type
    - Job type
    - Location
    - Salary range
    - Category

    Method: POST
    URL: /api/jobs/create-step1/
    Request Body:
    {
        "title": "Software Engineer",
        "hire_number": 3,
        "job_location_type": "remote",
        "job_type": "Full_time",
        "location": "US",
        "salary_range": "70001-100000",
        "category": 1
    }
    Response:
    - 201 Created: Returns the created job details.
    - 400 Bad Request: Returns validation errors.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = {
            "title": request.data.get("title"),
            "hire_number": request.data.get("hire_number"),
            "job_location_type": request.data.get("job_location_type"),
            "job_type": request.data.get("job_type"),
            "location": request.data.get("location"),
            "salary_range": request.data.get("salary_range"),
            "category": request.data.get("category"),
        }
        serializer = JobSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user, company=request.user.company)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateJobStep2APIView(APIView):
    """
    Endpoint to update the second step of a job.

    This step includes:
    - Job type
    - Experience levels
    - Weekly ranges
    - Shifts

    Method: PATCH
    URL: /api/jobs/<job_id>/create-step2/
    Request Body:
    {
        "job_type": "Full_time",
        "experience_levels": "1-3Years",
        "weekly_ranges": "mondayToFriday",
        "shifts": "morningShift"
    }
    Response:
    - 200 OK: Returns the updated job details.
    - 404 Not Found: If the job does not exist or the user is unauthorized.
    - 400 Bad Request: Returns validation errors.
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, job_id):
        job = Job.objects.filter(id=job_id, user=request.user).first()
        if not job:
            return Response({"error": "Job not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND)

        data = {
            "job_type": request.data.get("job_type"),
            "experience_levels": request.data.get("experience_levels"),
            "weekly_ranges": request.data.get("weekly_ranges"),
            "shifts": request.data.get("shifts"),
        }
        serializer = JobSerializer(job, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateJobStep3APIView(APIView):
    """
    Endpoint to update the third step of a job.

    This step includes:
    - Description
    - Responsibilities
    - Benefits

    Additionally, it extracts technical skills from the job description.

    Method: PATCH
    URL: /api/jobs/<job_id>/create-step3/
    Request Body:
    {
        "description": "We are looking for a skilled software engineer.",
        "responsibilities": "Develop and maintain software applications.",
        "benefits": "Health insurance, 401k"
    }
    Response:
    - 200 OK: Returns the updated job details and extracted skills.
    - 404 Not Found: If the job does not exist or the user is unauthorized.
    - 400 Bad Request: Returns validation errors.
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, job_id):
        job = Job.objects.filter(id=job_id, user=request.user).first()
        if not job:
            return Response({"error": "Job not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND)

        data = {
            "description": request.data.get("description"),
            "responsibilities": request.data.get("responsibilities"),
            "benefits": request.data.get("benefits"),
        }
        serializer = JobSerializer(job, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # Extract technical skills from the job description
            extracted_skills = extract_technical_skills(job.title, serializer.validated_data.get("description"))
            if extracted_skills:
                for skill_name in extracted_skills:
                    skill, _ = Skill.objects.get_or_create(name=skill_name)
                    job.extracted_skills.add(skill)

            return Response({
                "job": serializer.data,
                "extracted_skills": [skill.name for skill in job.extracted_skills.all()]
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateJobStep4APIView(APIView):
    """
    Endpoint to update the fourth step of a job.

    This step includes:
    - Requirements (skills selected from extracted skills)
    - Level (skill level)

    Additionally, it generates questions for the selected skills and triggers email notifications.

    Method: PATCH
    URL: /api/jobs/<job_id>/create-step4/
    Request Body:
    {
        "requirements": [1, 2],
        "level": "Mid"
    }
    Response:
    - 200 OK: Returns the updated job details and generated questions.
    - 404 Not Found: If the job does not exist or the user is unauthorized.
    - 400 Bad Request: Returns validation errors.
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request, job_id):
        job = Job.objects.filter(id=job_id, user=request.user).first()
        if not job:
            return Response({"error": "Job not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND)

        # Extract requirements and level from the request
        requirements = request.data.get("requirements", [])
        level = request.data.get("level")

        # Validate that all requirements are valid skill IDs
        try:
            skills = Skill.objects.filter(id__in=requirements)
            if len(skills) != len(requirements):
                return Response({"error": "One or more skill IDs are invalid."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Error validating skills: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Update the job's requirements and level
        job.requirements.set(skills)  # Use `set` to update ManyToManyField
        job.level = level
        job.save()

        # Generate questions for the selected skills
        generated_questions = []
        for skill in skills:
            result = generate_questions_task(job.title, level, skill.name, 5)
            if result['success']:
                generated_questions.extend(result['questions'])

        # Check if questions were successfully generated
        if generated_questions:
            return Response({
                "job": JobSerializer(job).data,
                "generated_questions": generated_questions,
                "message": "Questions generated successfully and emails sent."
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                "job": JobSerializer(job).data,
                "generated_questions": [],
                "message": "Failed to generate questions."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class JobOptionsAPIView(APIView):
    """
    Endpoint to fetch job-related options such as categories, salary ranges, locations, and job location types.
    """
    def get(self, request):
        categories = SkillCategory.objects.values('id', 'name')
        salary_ranges = dict(Job._meta.get_field('salary_range').choices)
        job_location_types = dict(Job._meta.get_field('job_location_type').choices)
        countries_list = [
            {
                'code': code,
                'name': name,
                'flag_url': f'https://flagcdn.com/w40/{code.lower()}.png'  # Flag URL
            }
            for code, name in countries
        ]

        return Response({
            "categories": list(categories),
            "salary_ranges": salary_ranges,
            "job_location_types": job_location_types,
            "locations": countries_list,
        })
