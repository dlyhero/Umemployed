from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from ..models import Company, Interview
from job.models import Rating 
from job.models import Job, Application, Shortlist  # Import Shortlist model
from resume.models import Resume, WorkExperience
from transactions.models import Transaction
from users.models import User
from rest_framework.permissions import IsAuthenticated,BasePermission
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import CompanySerializer
from django.db.models import Count
from ..forms import RatingForm
from django.http import HttpResponseForbidden
import random
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string

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
        serializer = CompanySerializer(data=request.data)  # Removed files argument
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
    permission_classes = []
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
    permission_classes = []
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
    permission_classes = []

    @swagger_auto_schema(
        operation_description="Retrieve jobs posted by the company",
        responses={200: "Jobs retrieved successfully", 404: "Not Found"}
    )
    def get(self, request, company_id):
        """
        Handle GET requests to retrieve jobs posted by the company.
        """
        company = get_object_or_404(Company, id=company_id)
        # Ensure the query filters jobs by the company and job_creation_is_complete is True
        jobs = Job.objects.filter(company=company, job_creation_is_complete=True).order_by('-created_at')
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
                "application_id": app.id,
                "job_id": app.job.id,  # Added job_id
                "job_title": app.job.title,
                "user_id": app.user.id,  # Added user_id
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
            "job_id": application.job.id,  # Added job_id
            "job_title": application.job.title,
            "user_id": application.user.id,  # Added user_id
            "user": application.user.username,
            "status": application.status,
            "quiz_score": application.quiz_score,
            "matching_percentage": application.matching_percentage,
            "overall_match_percentage": application.overall_match_percentage,
            "resume": resume.id if resume else None,
            "created_at": application.created_at,
            "updated_at": application.updated_at,
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

        # Calculate match percentage and overall score for each application
        for application in applications:
            user = application.user
            resume = Resume.objects.filter(user=user).first()  # Avoid DoesNotExist error

            if resume:  # Check if the user has a resume
                applicant_skills = set(resume.skills.all())
                job_skills = set(job.requirements.all())
                match_percentage, _ = application.calculate_skill_match(applicant_skills, job_skills)
                application.matching_percentage = match_percentage

                # Calculate the overall score using match percentage and quiz score
                quiz_score = application.quiz_score
                overall_score = match_percentage * 0.7 + (quiz_score / 10) * 0.3
                application.overall_score = overall_score
            else:
                # Handle cases where no resume exists
                application.matching_percentage = 0
                application.overall_score = application.quiz_score / 10 * 0.3  # Only quiz score

        # Sort applications based on quiz score, matching percentage, and randomly if there's a tie
        applications = sorted(applications, key=lambda x: (x.quiz_score, x.matching_percentage, random.random()), reverse=True)

        # Select top 5 applications and the next 5 for the waiting list
        top_5_applications = applications[:5]
        waiting_list_applications = applications[5:10]

        application_data = {
            "top_5_candidates": [
                {
                    "application_id": app.id,
                    "job_id": app.job.id,
                    "user_id": app.user.id,
                    "user": app.user.username,
                    "status": app.status,
                    "quiz_score": app.quiz_score,
                    "matching_percentage": app.matching_percentage,
                    "overall_match_percentage": app.overall_match_percentage,
                    "created_at": app.created_at,
                    "updated_at": app.updated_at,
                }
                for app in top_5_applications
            ],
            "waiting_list_candidates": [
                {
                    "application_id": app.id,
                    "job_id": app.job.id,
                    "user_id": app.user.id,
                    "user": app.user.username,
                    "status": app.status,
                    "quiz_score": app.quiz_score,
                    "matching_percentage": app.matching_percentage,
                    "overall_match_percentage": app.overall_match_percentage,
                    "created_at": app.created_at,
                    "updated_at": app.updated_at,
                }
                for app in waiting_list_applications
            ],
        }

        return Response(application_data, status=status.HTTP_200_OK)

class ShortlistedCandidatesAPIView(APIView):
    """
    API view to retrieve shortlisted candidates for a specific job.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve shortlisted candidates for a specific job",
        responses={200: "Shortlisted candidates retrieved successfully", 404: "Not Found"}
    )
    def get(self, request, company_id, job_id):
        """
        Handle GET requests to retrieve shortlisted candidates for a specific job.
        """
        company = get_object_or_404(Company, id=company_id, user=request.user)
        job = get_object_or_404(Job, id=job_id, company=company)
        shortlisted_candidates = Shortlist.objects.filter(job=job)

        candidate_data = [
            {
                "candidate_id": shortlist.candidate.id,
                "candidate_name": shortlist.candidate.get_full_name(),
                "candidate_email": shortlist.candidate.email,
                "job_id": shortlist.job.id,
                "job_title": shortlist.job.title,
                "shortlisted_at": shortlist.created_at,
                "application": {
                    "application_id": application.id,
                    "status": application.status,
                    "quiz_score": application.quiz_score,
                    "matching_percentage": application.matching_percentage,
                    "overall_match_percentage": application.overall_match_percentage,
                } if (application := Application.objects.filter(user=shortlist.candidate, job=job).first()) else None
            }
            for shortlist in shortlisted_candidates
        ]

        return Response(candidate_data, status=status.HTTP_200_OK)

@method_decorator(csrf_exempt, name='dispatch')
class ShortlistCandidateAPIView(APIView):
    """
    API view to shortlist a candidate for a specific job.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Shortlist a candidate for a specific job",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'candidate_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the candidate to shortlist'),
            },
        ),
        responses={201: "Candidate shortlisted successfully", 400: "Bad Request", 404: "Not Found"}
    )
    def post(self, request, company_id, job_id):
        """
        Handle POST requests to shortlist a candidate.
        """
        company = get_object_or_404(Company, id=company_id, user=request.user)
        job = get_object_or_404(Job, id=job_id, company=company)
        candidate_id = request.data.get('candidate_id')

        if not candidate_id:
            return Response({"error": "Candidate ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        candidate = get_object_or_404(User, id=candidate_id)

        # Check if the candidate is already shortlisted
        if Shortlist.objects.filter(job=job, candidate=candidate).exists():
            return Response({"error": "Candidate is already shortlisted for this job."}, status=status.HTTP_400_BAD_REQUEST)

        # Create a new shortlist entry
        Shortlist.objects.create(recruiter=request.user, candidate=candidate, job=job)
        return Response({"message": "Candidate shortlisted successfully."}, status=status.HTTP_201_CREATED)

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

        # Validate required fields
        if not date:
            return Response({"error": "The 'date' field is required."}, status=status.HTTP_400_BAD_REQUEST)
        if not time:
            return Response({"error": "The 'time' field is required."}, status=status.HTTP_400_BAD_REQUEST)

        candidate = get_object_or_404(User, id=candidate_id)
        job = get_object_or_404(Job, id=job_id)
        interview = Interview.objects.create(
            candidate=candidate,
            date=date,
            time=time,
            timezone=timezone,
            note=note,
            meeting_link=f"https://umemployed.com/interview/{job.id}"
        )
        return Response({"message": "Interview created successfully", "interview_id": interview.id}, status=status.HTTP_201_CREATED)

class RateCandidateAPIView(APIView):
    """
    API view to rate a candidate.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Rate a candidate",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'professionalism': openapi.Schema(type=openapi.TYPE_STRING, description='Professionalism rating'),
                'skills': openapi.Schema(type=openapi.TYPE_STRING, description='Skills rating'),
                'communication': openapi.Schema(type=openapi.TYPE_STRING, description='Communication rating'),
                'teamwork': openapi.Schema(type=openapi.TYPE_STRING, description='Teamwork rating'),
                'reliability': openapi.Schema(type=openapi.TYPE_STRING, description='Reliability rating'),
                'stars': openapi.Schema(type=openapi.TYPE_INTEGER, description='Star rating (1-5)'),
                'review': openapi.Schema(type=openapi.TYPE_STRING, description='Review text'),
            },
        ),
        responses={
            200: "Candidate rated successfully",
            403: "Forbidden",
            400: "Bad Request"
        }
    )
    def post(self, request, candidate_id):
        """
        Handle POST requests to rate a candidate.
        """
        candidate = get_object_or_404(User, id=candidate_id)
        endorser = request.user

        # Ensure the endorser and candidate have a past relationship in a company or matching email domains
        candidate_companies = WorkExperience.objects.filter(user=candidate).values_list('company_name', flat=True)
        endorser_companies = WorkExperience.objects.filter(user=endorser).values_list('company_name', flat=True)
        candidate_email_domain = candidate.email.split('@')[-1]
        endorser_email_domain = endorser.email.split('@')[-1]

        if not (set(candidate_companies).intersection(set(endorser_companies)) or candidate_email_domain == endorser_email_domain):
            return Response({"error": "You are not allowed to rate this candidate."}, status=status.HTTP_403_FORBIDDEN)

        # Check if a rating already exists
        rating = Rating.objects.filter(candidate=candidate, endorser=endorser).first()

        # Extract data from the request
        professionalism = request.data.get('professionalism')
        skills = request.data.get('skills')
        communication = request.data.get('communication')
        teamwork = request.data.get('teamwork')
        reliability = request.data.get('reliability')
        stars = request.data.get('stars')
        review = request.data.get('review')

        # Validate required fields
        if not all([professionalism, skills, communication, teamwork, reliability, stars]):
            return Response({"error": "All fields are required."}, status=status.HTTP_400_BAD_REQUEST)

        # Create or update the rating
        if not rating:
            rating = Rating(candidate=candidate, endorser=endorser)
        rating.professionalism = professionalism
        rating.skills = skills
        rating.communication = communication
        rating.teamwork = teamwork
        rating.reliability = reliability
        rating.stars = stars
        rating.review = review
        rating.save()

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
        Handle GET requests to retrieve users related to a company.
        """
        current_user = request.user
        user_companies = WorkExperience.objects.filter(user=current_user).values_list('company_name', flat=True)
        current_user_email_domain = current_user.email.split('@')[-1]

        # Query related users based on work experiences
        related_users = User.objects.filter(
            work_experiences__company_name__in=user_companies
        ).distinct().exclude(id=current_user.id)

        # Include users with matching email domains
        related_users_by_email = User.objects.filter(
            email__endswith=current_user_email_domain
        ).distinct().exclude(id=current_user.id)

        # Combine both querysets
        related_users = related_users | related_users_by_email

        user_data = [
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            }
            for user in related_users.distinct()
        ]

        return Response(user_data, status=status.HTTP_200_OK)

class CandidateEndorsementsAPIView(APIView):
    """
    API view to retrieve endorsements for a candidate.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve endorsements for a candidate",
        responses={
            200: "Endorsements retrieved successfully",
            404: "Not Found"
        }
    )
    def get(self, request, candidate_id):
        """
        Handle GET requests to retrieve endorsements for a candidate.
        """
        candidate = get_object_or_404(User, id=candidate_id)

        # Check if the user has a completed transaction for this candidate
        has_paid = Transaction.objects.filter(
            user=request.user,
            candidate=candidate,
            status='completed'
        ).exists()

        if not has_paid:
            return Response({"error": "You must complete payment to view endorsements."}, status=status.HTTP_403_FORBIDDEN)

        # Retrieve endorsements for the candidate
        endorsements = Rating.objects.filter(candidate=candidate)
        endorsements_data = [
            {
                "id": endorsement.id,
                "endorser": endorsement.endorser.username,
                "stars": endorsement.stars,
                "review": endorsement.review,
                "professionalism": endorsement.professionalism,
                "skills": endorsement.skills,
                "communication": endorsement.communication,
                "teamwork": endorsement.teamwork,
                "reliability": endorsement.reliability,
            }
            for endorsement in endorsements
        ]

        return Response(endorsements_data, status=status.HTTP_200_OK)

class CheckPaymentStatusAPIView(APIView):
    """
    API view to check if payment for viewing endorsements has been completed.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Check if payment for viewing endorsements has been completed",
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    "has_paid": openapi.Schema(type=openapi.TYPE_BOOLEAN, description="Whether the payment has been completed"),
                },
            ),
            404: "Not Found"
        }
    )
    def get(self, request, candidate_id):
        """
        Handle GET requests to check payment status for a candidate.
        """
        candidate = get_object_or_404(User, id=candidate_id)

        # Check if the user has a completed transaction for this candidate
        has_paid = Transaction.objects.filter(
            user=request.user,
            candidate=candidate,
            status='completed'
        ).exists()

        return Response({"has_paid": has_paid}, status=status.HTTP_200_OK)

class UnshortlistCandidateAPIView(APIView):
    """
    API view to unshortlist a candidate for a specific job.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Unshortlist a candidate for a specific job",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'candidate_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID of the candidate to unshortlist'),
            },
            required=['candidate_id'],
        ),
        responses={200: "Candidate unshortlisted successfully", 400: "Bad Request", 404: "Not Found"}
    )
    def post(self, request, company_id, job_id):
        company = get_object_or_404(Company, id=company_id, user=request.user)
        job = get_object_or_404(Job, id=job_id, company=company)
        candidate_id = request.data.get('candidate_id')

        if not candidate_id:
            return Response({"error": "Candidate ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        candidate = get_object_or_404(User, id=candidate_id)

        shortlist = Shortlist.objects.filter(job=job, candidate=candidate).first()
        if not shortlist:
            return Response({"error": "Candidate is not shortlisted for this job."}, status=status.HTTP_400_BAD_REQUEST)

        shortlist.delete()
        return Response({"message": "Candidate unshortlisted successfully."}, status=status.HTTP_200_OK)

class MyShortlistedJobsAPIView(APIView):
    """
    API view to retrieve jobs where the specified user has been shortlisted.
    """
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Retrieve jobs where the specified user has been shortlisted",
        responses={200: "Shortlisted jobs retrieved successfully"}
    )
    def get(self, request, user_id):
        # Short-circuit for schema generation (e.g., drf_yasg)
        if getattr(self, 'swagger_fake_view', False):
            return Response([])

        """
        Handle GET requests to retrieve jobs where the user has been shortlisted.
        """
        # Only allow the user themselves or an admin to view this
        if request.user.id != user_id and not request.user.is_staff:
            return Response({"detail": "Not authorized."}, status=status.HTTP_403_FORBIDDEN)

        user = get_object_or_404(User, id=user_id)
        shortlisted = Shortlist.objects.filter(candidate=user).select_related('job', 'job__company')
        jobs_data = [
            {
                "job_id": s.job.id,
                "job_title": s.job.title,
                "company_id": s.job.company.id,
                "company_name": s.job.company.name,
                "shortlisted_at": s.created_at,
            }
            for s in shortlisted
        ]
        return Response(jobs_data, status=status.HTTP_200_OK)

def update_and_notify_top10(job):
    """
    Helper function to update top 10 candidates and send emails as needed.
    Should be called after a new application is created for a job.
    """
    applications = Application.objects.filter(job=job)
    # Calculate scores
    for application in applications:
        user = application.user
        resume = Resume.objects.filter(user=user).first()
        if resume:
            applicant_skills = set(resume.skills.all())
            job_skills = set(job.requirements.all())
            match_percentage, _ = application.calculate_skill_match(applicant_skills, job_skills)
            application.matching_percentage = match_percentage
            quiz_score = application.quiz_score
            # Use overall_match_percentage instead of overall_score
            application.overall_match_percentage = application.overall_match_percentage  # Already set by model logic
        else:
            application.matching_percentage = 0
            application.overall_match_percentage = application.quiz_score / 10 * 0.3  # Only quiz score
        application.save(update_fields=['matching_percentage', 'overall_match_percentage'])

    # Sort applications by overall_match_percentage, then quiz_score, then random
    sorted_apps = sorted(
        applications,
        key=lambda x: (float(x.overall_match_percentage), x.quiz_score, random.random()),
        reverse=True
    )
    # Get previous top 10 for comparison
    prev_top10_ids = set(Application.objects.filter(job=job, top10_flag=True).values_list('id', flat=True))
    # Mark all as not in top 10
    Application.objects.filter(job=job, top10_flag=True).update(top10_flag=False)

    # Mark new top 10 and send emails
    new_top10_ids = set()
    for idx, app in enumerate(sorted_apps[:10]):
        app.top10_flag = True
        app.save(update_fields=['top10_flag'])
        new_top10_ids.add(app.id)
        # Send emails based on position
        if idx < 5:
            # Top 5
            if app.id not in prev_top10_ids or idx < 5 and app.id not in set(Application.objects.filter(job=job, top10_flag=True, top5_flag=True).values_list('id', flat=True)):
                subject = "Congratulations! You're among the top candidates"
                html_message = render_to_string(
                    'emails/top5_candidate.html',
                    {
                        'username': app.user.username,
                        'job_title': job.title,
                        'company_name': job.company.name,
                    }
                )
                send_mail(
                    subject,
                    '',  # Plain text fallback (optional)
                    settings.DEFAULT_FROM_EMAIL,
                    [app.user.email],
                    html_message=html_message,
                    fail_silently=True,
                )
            app.top5_flag = True
            app.save(update_fields=['top5_flag'])
        else:
            # Waiting list (6-10)
            if app.id not in prev_top10_ids or app.top5_flag:
                subject = f"Update: Your application status for {job.title}"
                html_message = render_to_string(
                    'emails/waiting_list_candidate.html',
                    {
                        'username': app.user.username,
                        'job_title': job.title,
                        'company_name': job.company.name,
                    }
                )
                send_mail(
                    subject,
                    '',  # Plain text fallback (optional)
                    settings.DEFAULT_FROM_EMAIL,
                    [app.user.email],
                    html_message=html_message,
                    fail_silently=True,
                )
            app.top5_flag = False
            app.save(update_fields=['top5_flag'])

    # Send sorry email to those who dropped out of top 10
    dropped_ids = prev_top10_ids - new_top10_ids
    for app in Application.objects.filter(id__in=dropped_ids):
        subject = f"Update: Your application status for {job.title}"
        html_message = render_to_string(
            'emails/sorry_candidate.html',
            {
                'username': app.user.username,
                'job_title': job.title,
                'company_name': job.company.name,
            }
        )
        send_mail(
            subject,
            '',  # Plain text fallback (optional)
            settings.DEFAULT_FROM_EMAIL,
            [app.user.email],
            html_message=html_message,
            fail_silently=True,
        )
        app.top5_flag = False
        app.top10_flag = False
        app.save(update_fields=['top5_flag', 'top10_flag'])

# --- Usage Example ---
# In your application creation view (not shown), after saving a new Application:
# update_and_notify_top10(job)

# You must add BooleanFields to Application model: top5_flag and top10_flag (default False)
