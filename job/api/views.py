from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from ..models import Job, Application, SavedJob
from ..tasks import generate_questions_task
from ..job_description_algorithm import extract_technical_skills
from .serializers import JobSerializer, ApplicationSerializer, SavedJobSerializer

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

class CreateJobAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = JobSerializer(data=request.data)
        if serializer.is_valid():
            # Ensure the user and company are set correctly
            serializer.save(user=request.user, company=request.user.company)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CreateJobStep1APIView(APIView):
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
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CreateJobStep3APIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, job_id):
        job = Job.objects.filter(id=job_id, user=request.user).first()
        if not job:
            return Response({"error": "Job not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND)

        data = {
            "requirements": request.data.get("requirements"),
            "level": request.data.get("level"),
        }
        serializer = JobSerializer(job, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
