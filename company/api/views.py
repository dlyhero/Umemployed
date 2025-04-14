from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models import Company, Interview
from job.models import Job, Application
from resume.models import Resume, WorkExperience
from transactions.models import Transaction
from users.models import User
from rest_framework.permissions import IsAuthenticated,BasePermission
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import CompanySerializer
from django.db.models import Count

class IsCompanyOwner(BasePermission):
    """
    Custom permission to allow only the owner of the company to access certain views.
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user

class CreateCompanyAPIView(APIView):
    """
    API view to create a new company.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create a new company",
        request_body=CompanySerializer,
        responses={
            201: CompanySerializer,
            400: "Bad Request"
        }
    )
    def post(self, request):
        """
        Handle POST requests to create a company.
        """
        serializer = CompanySerializer(data=request.data, files=request.FILES)  # Pass request.FILES for file uploads
        if serializer.is_valid():
            serializer.save(user=request.user)
            request.user.has_company = True
            request.user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UpdateCompanyAPIView(APIView):
    """
    API view to update an existing company.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Update an existing company",
        request_body=CompanySerializer,
        responses={
            200: CompanySerializer,
            400: "Bad Request",
            404: "Not Found"
        }
    )
    def put(self, request, company_id):
        """
        Handle PUT requests to update a company.
        """
        company = get_object_or_404(Company, id=company_id, user=request.user)
        serializer = CompanySerializer(company, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CompanyDetailsAPIView(APIView):
    """
    API view to retrieve details of a specific company.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve details of a specific company",
        responses={
            200: CompanySerializer,
            404: "Not Found"
        }
    )
    def get(self, request, company_id):
        """
        Handle GET requests to retrieve company details.
        """
        company = get_object_or_404(Company, id=company_id)
        serializer = CompanySerializer(company)
        return Response(serializer.data, status=status.HTTP_200_OK)

class CompanyListAPIView(APIView):
    """
    API view to list all companies.
    """
    @swagger_auto_schema(
        operation_description="List all companies",
        responses={200: "Companies retrieved successfully"}
    )
    def get(self, request):
        """
        Handle GET requests to list all companies.
        """
        companies = Company.objects.annotate(available_jobs=Count('job'))
        company_data = [
            {
                "id": company.id,
                "name": company.name,
                "available_jobs": company.available_jobs
            }
            for company in companies
        ]
        return Response(company_data, status=status.HTTP_200_OK)

class CompanyDashboardAPIView(APIView):
    """
    API view to retrieve the dashboard data for a company.
    """
    permission_classes = [IsAuthenticated, IsCompanyOwner]

    @swagger_auto_schema(
        operation_description="Retrieve the dashboard data for the company",
        responses={
            200: "Dashboard data retrieved successfully",
            403: "Forbidden - You are not the owner of this company",
            404: "Not Found"
        }
    )
    def get(self, request, company_id):
        """
        Handle GET requests to retrieve company dashboard data.
        """
        company = get_object_or_404(Company, id=company_id)
        self.check_object_permissions(request, company)
        jobs = Job.objects.filter(company=company).order_by('-created_at')
        job_data = [
            {
                "id": job.id,
                "title": job.title,
                "application_count": Application.objects.filter(job=job).count()
            }
            for job in jobs
        ]
        return Response({
            "company": {
                "id": company.id,
                "name": company.name,
                "industry": company.industry,
                "size": company.size,
            },
            "jobs": job_data
        }, status=status.HTTP_200_OK)

class CompanyAnalyticsAPIView(APIView):
    """
    API view to retrieve analytics data for a company.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve analytics data for the company",
        responses={200: "Analytics data retrieved successfully", 404: "Not Found"}
    )
    def get(self, request, company_id):
        """
        Handle GET requests to retrieve company analytics data.
        """
        company = get_object_or_404(Company, id=company_id, user=request.user)
        analytics_data = {
            "total_jobs": Job.objects.filter(company=company).count(),
            "total_applications": Application.objects.filter(job__company=company).count(),
        }
        return Response(analytics_data, status=status.HTTP_200_OK)

class ViewMyJobsAPIView(APIView):
    """
    API view to retrieve jobs posted by a company.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve jobs posted by the company",
        responses={200: "Jobs retrieved successfully", 404: "Not Found"}
    )
    def get(self, request, company_id):
        """
        Handle GET requests to retrieve jobs posted by the company.
        """
        company = get_object_or_404(Company, id=company_id)
        # Ensure the query filters jobs by the company
        jobs = Job.objects.filter(company=company).order_by('-created_at')
        job_data = [
            {
                "id": job.id,
                "title": job.title,
                "application_count": Application.objects.filter(job=job).count()
            }
            for job in jobs
        ]
        return Response(job_data, status=status.HTTP_200_OK)

class ViewApplicationsAPIView(APIView):
    """
    API view to retrieve applications for jobs posted by a company.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve applications for jobs posted by the company",
        responses={200: "Applications retrieved successfully", 404: "Not Found"}
    )
    def get(self, request, company_id):
        """
        Handle GET requests to retrieve applications for jobs posted by the company.
        """
        company = get_object_or_404(Company, id=company_id, user=request.user)
        jobs = Job.objects.filter(company=company)
        applications = Application.objects.filter(job__in=jobs)
        application_data = [
            {
                "id": app.id,
                "job_title": app.job.title,
                "user": app.user.username,
                "status": app.status
            }
            for app in applications
        ]
        return Response(application_data, status=status.HTTP_200_OK)

class ApplicationDetailsAPIView(APIView):
    """
    API view to retrieve details of a specific application.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve details of a specific application",
        responses={200: "Application details retrieved successfully", 404: "Not Found"}
    )
    def get(self, request, application_id):
        """
        Handle GET requests to retrieve application details.
        """
        application = get_object_or_404(Application, id=application_id)
        resume = Resume.objects.filter(user=application.user).first()
        data = {
            "application_id": application.id,
            "job_title": application.job.title,
            "user": application.user.username,
            "resume": resume.id if resume else None,
        }
        return Response(data, status=status.HTTP_200_OK)

class JobApplicationsViewAPIView(APIView):
    """
    API view to retrieve applications for a specific job.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve applications for a specific job",
        responses={200: "Job applications retrieved successfully", 404: "Not Found"}
    )
    def get(self, request, company_id, job_id):
        """
        Handle GET requests to retrieve applications for a specific job.
        """
        company = get_object_or_404(Company, id=company_id, user=request.user)
        job = get_object_or_404(Job, id=job_id, company=company)
        applications = Application.objects.filter(job=job)
        application_data = [
            {
                "id": app.id,
                "user": app.user.username,
                "status": app.status
            }
            for app in applications
        ]
        return Response(application_data, status=status.HTTP_200_OK)

class CreateInterviewAPIView(APIView):
    """
    API view to create an interview for a candidate.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create an interview for a candidate",
        responses={201: "Interview created successfully", 400: "Bad Request"}
    )
    def post(self, request):
        """
        Handle POST requests to create an interview.
        """
        candidate_id = request.data.get('candidate_id')
        job_id = request.data.get('job_id')
        date = request.data.get('date')
        time = request.data.get('time')
        timezone = request.data.get('timezone')
        note = request.data.get('note')

        candidate = get_object_or_404(User, id=candidate_id)
        job = get_object_or_404(Job, id=job_id)
        interview = Interview.objects.create(
            candidate=candidate,
            date=date,
            time=time,
            timezone=timezone,
            note=note,
            meeting_link=f"http://example.com/interview/{job.id}"
        )
        return Response({"message": "Interview created successfully", "interview_id": interview.id}, status=status.HTTP_201_CREATED)

class RateCandidateAPIView(APIView):
    """
    API view to rate a candidate.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Rate a candidate",
        responses={200: "Candidate rated successfully", 403: "Forbidden"}
    )
    def post(self, request, candidate_id):
        """
        Handle POST requests to rate a candidate.
        """
        candidate = get_object_or_404(User, id=candidate_id)
        rating = request.data.get('rating')
        # Logic to save the rating
        return Response({"message": "Candidate rated successfully"}, status=status.HTTP_200_OK)

class CompanyRelatedUsersAPIView(APIView):
    """
    API view to retrieve users related to a company.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve users related to the company",
        responses={200: "Related users retrieved successfully"}
    )
    def get(self, request):
        """
        Handle GET requests to retrieve users related to the company.
        """
        current_user = request.user
        related_users = User.objects.filter(work_experiences__company_name__in=current_user.work_experiences.values_list('company_name', flat=True)).distinct()
        user_data = [{"id": user.id, "username": user.username} for user in related_users]
        return Response(user_data, status=status.HTTP_200_OK)

class StartPaymentForEndorsementAPIView(APIView):
    """
    API view to start payment for viewing endorsements.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Start payment for viewing endorsements",
        responses={200: "Payment started successfully", 403: "Forbidden"}
    )
    def post(self, request, candidate_id):
        """
        Handle POST requests to start payment for viewing endorsements.
        """
        candidate = get_object_or_404(User, id=candidate_id)
        # Logic to initiate payment
        return Response({"message": "Payment started successfully"}, status=status.HTTP_200_OK)
