import json
import logging
import random
import re

import openai
from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django_countries import countries  # Import the correct iterable for countries
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from company.api.views import update_and_notify_top10  # Add this import
from notifications.models import Notification
from notifications.utils import notify_user, notify_user_declined
from resume.models import Skill
from transactions.api.permissions import HasActiveSubscription
from transactions.models import Subscription

from ..generate_skills import generate_questions_task
from ..job_description_algorithm import extract_technical_skills
from ..models import (
    ApplicantAnswer,
    Application,
    Company,
    CompletedSkills,
    Job,
    RetakeRequest,
    SavedJob,
    Shortlist,
    SkillCategory,
    SkillQuestion,
    User,
)
from ..tasks import generate_questions_task, smart_generate_questions_task
from .serializers import ApplicationSerializer, JobSerializer, SavedJobSerializer

logger = logging.getLogger(__name__)


class JobListAPIView(ListAPIView):
    queryset = Job.objects.filter(job_creation_is_complete=True)
    serializer_class = JobSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class JobDetailAPIView(RetrieveAPIView):
    queryset = Job.objects.all()
    serializer_class = JobSerializer

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class ApplyJobAPIView(APIView):
    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        user = request.user

        # Check if the user has already applied for this job
        existing_application = Application.objects.filter(user=user, job=job).first()

        if existing_application:
            return Response(
                {"message": "You have already applied for this job."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Create a new application
        application = Application.objects.create(user=user, job=job)
        application.save()

        return Response(
            {"message": "Job application submitted successfully."}, status=status.HTTP_201_CREATED
        )


class SaveJobAPIView(APIView):
    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        user = request.user

        # Check if the job is already saved
        saved_job, created = SavedJob.objects.get_or_create(user=user, job=job)

        if created:
            return Response({"message": "Job saved successfully."}, status=status.HTTP_201_CREATED)
        else:
            saved_job.delete()
            return Response({"message": "Job removed successfully."}, status=status.HTTP_200_OK)


class WithdrawApplicationAPIView(APIView):
    def delete(self, request, job_id):
        user = request.user
        job = get_object_or_404(Job, id=job_id)
        application = Application.objects.filter(user=user, job=job).first()
        if application:
            application.delete()
            # Notify recruiter/company owner
            if job.company and job.company.user:
                Notification.objects.create(
                    user=job.company.user,
                    notification_type=Notification.JOB_APPLICATION,
                    message=f"{user.get_full_name() or user.username} has withdrawn their application for '{job.title}'.",
                )
            return Response(
                {"message": "Your application has been withdrawn."}, status=status.HTTP_200_OK
            )
        else:
            return Response(
                {"message": "You haven't applied for this job."}, status=status.HTTP_400_BAD_REQUEST
            )


class ShortlistCandidateAPIView(APIView):
    def post(self, request, job_id, candidate_id):
        job = get_object_or_404(Job, id=job_id)
        candidate = get_object_or_404(User, id=candidate_id)
        recruiter = request.user
        # Check if the candidate is already shortlisted for the job
        if Shortlist.objects.filter(recruiter=recruiter, candidate=candidate, job=job).exists():
            return Response(
                {"message": "Candidate is already shortlisted for this job."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        Shortlist.objects.create(recruiter=recruiter, candidate=candidate, job=job)
        # Notify candidate
        Notification.objects.create(
            user=candidate,
            notification_type=Notification.JOB_APPLICATION,
            message=f"You have been shortlisted for the job '{job.title}' at {job.company.name if job.company else ''}.",
        )
        return Response(
            {"message": "Candidate has been shortlisted successfully."},
            status=status.HTTP_201_CREATED,
        )


class DeclineCandidateAPIView(APIView):
    def post(self, request, job_id, candidate_id):
        job = get_object_or_404(Job, id=job_id)
        candidate = get_object_or_404(User, id=candidate_id)
        recruiter = request.user

        # Check if the recruiter is associated with the job
        company = get_object_or_404(Company, user=recruiter)
        if job.company != company:
            return Response(
                {"message": "You are not authorized to decline this candidate."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Get the application object
        application = get_object_or_404(Application, job=job, user=candidate)

        # Delete the application object
        application.delete()

        # Send notification to the candidate
        notify_user_declined(
            candidate,
            f"Your application for the job '{job.title}' has been declined.",
            Notification.JOB_APPLICATION,
        )

        # Send email to the candidate
        subject = "Application Declined"
        message = f"""
                    Dear {candidate.get_full_name()},

                    Thank you for your interest in the {job.title} position at {company.name}. After careful consideration, we regret to inform you that we will not be moving forward with your application at this time.

                    We truly appreciate the effort you put into your application and encourage you to apply for future opportunities that align with your qualifications. Thank you again for your time and interest in joining our team.

                    Wishing you the very best in your job search.

                    Warm regards,
                    {company.name}
                    """
        from_email = settings.DEFAULT_FROM_EMAIL
        send_mail(subject, message, from_email, [candidate.email])

        return Response(
            {"message": "Candidate has been declined successfully."}, status=status.HTTP_200_OK
        )


class SavedJobsListAPIView(ListAPIView):
    serializer_class = JobSerializer

    def get_queryset(self):
        # Short-circuit for Swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Job.objects.none()
        saved_jobs = SavedJob.objects.filter(user=self.request.user).select_related("job")
        return Job.objects.filter(id__in=saved_jobs.values_list("job_id", flat=True))

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class GenerateQuestionsAPIView(APIView):
    def post(self, request):
        job_title = request.data.get("job_title")
        entry_level = request.data.get("entry_level")
        skill_name = request.data.get("skill_name")
        questions_per_skill = request.data.get("questions_per_skill", 5)

        generate_questions_task.delay(job_title, entry_level, skill_name, questions_per_skill)
        return Response(
            {"message": "Question generation started."}, status=status.HTTP_202_ACCEPTED
        )


class ExtractTechnicalSkillsAPIView(APIView):
    def post(self, request):
        job_title = request.data.get("job_title")
        job_description = request.data.get("job_description")

        if not job_title or not job_description:
            return Response(
                {"error": "Job title and description are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        skills = extract_technical_skills(job_title, job_description)
        return Response({"skills": skills}, status=status.HTTP_200_OK)


class AppliedJobsListAPIView(ListAPIView):
    serializer_class = ApplicationSerializer

    def get_queryset(self):
        # Short-circuit for Swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Application.objects.none()
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

    permission_classes = [IsAuthenticated, HasActiveSubscription]
    required_user_type = "recruiter"

    def post(self, request):
        user = request.user
        subscription = Subscription.objects.filter(
            user=user, user_type="recruiter", is_active=True
        ).first()
        if not subscription:
            return Response(
                {"message": "No active recruiter subscription found."},
                status=status.HTTP_403_FORBIDDEN,
            )
        # Check daily posting limit
        if not subscription.can_perform_action("posting"):
            return Response(
                {
                    "message": "You have reached your daily job posting limit for your subscription tier."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        # Example: Only allow AI job description for premium recruiters
        if request.data.get("use_ai_job_description"):
            if not subscription.has_feature("ai_job_description"):
                return Response(
                    {"message": "Your subscription does not include AI job description feature."},
                    status=status.HTTP_403_FORBIDDEN,
                )

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
            serializer.save(user=user, company=user.company)
            subscription.increment_usage("posting")  # Increment usage after successful post
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
            return Response(
                {"error": "Job not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND
            )

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
            return Response(
                {"error": "Job not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND
            )

        data = {
            "description": request.data.get("description"),
            "responsibilities": request.data.get("responsibilities"),
            "benefits": request.data.get("benefits"),
        }
        serializer = JobSerializer(job, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()

            # Extract technical skills from the job description
            extracted_skills = extract_technical_skills(
                job.title, serializer.validated_data.get("description")
            )
            if extracted_skills:
                for skill_name in extracted_skills:
                    skill, _ = Skill.objects.get_or_create(name=skill_name)
                    job.extracted_skills.add(skill)

            return Response(
                {
                    "job": serializer.data,
                    "extracted_skills": [skill.name for skill in job.extracted_skills.all()],
                },
                status=status.HTTP_200_OK,
            )
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
            return Response(
                {"error": "Job not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND
            )

        # Extract requirements and level from the request
        requirements = request.data.get("requirements", [])
        level = request.data.get("level")

        # Validate that all requirements are valid skill IDs
        try:
            skills = Skill.objects.filter(id__in=requirements)
            if len(skills) != len(requirements):
                return Response(
                    {"error": "One or more skill IDs are invalid."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {"error": f"Error validating skills: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Update the job's requirements and level
        job.requirements.set(skills)  # Use `set` to update ManyToManyField
        job.level = level
        job.is_available = True  # Set is_available to True
        job.save()

        # Notify recruiter that job is now available
        Notification.objects.create(
            user=request.user,
            notification_type=Notification.NEW_JOB_POSTED,
            message=f"Your job '{job.title}' is now available and visible to candidates.",
        )

        # Generate questions for the selected skills using smart generation
        for skill in skills:
            smart_generate_questions_task.delay(job.id, skill.id, level, 5)

        return Response(
            {
                "job": JobSerializer(job).data,
                "message": "Job creation step 4 completed. Smart question generation started in background.",
            },
            status=status.HTTP_200_OK,
        )


class JobOptionsAPIView(APIView):
    """
    Endpoint to fetch job-related options such as categories, salary ranges, locations, job location types,
    experience levels, weekly ranges, shifts, and job types.
    """

    def get(self, request):
        # Group categories by name (case-insensitive), pick the most popular in each group
        from collections import Counter, defaultdict

        categories_qs = SkillCategory.objects.all()
        # Build a mapping: lowercased name -> list of categories
        name_map = defaultdict(list)
        for cat in categories_qs:
            name_map[cat.name.strip().lower()].append(cat)
        # For each group, pick the category with the most jobs
        unique_categories = []
        for group in name_map.values():
            if len(group) == 1:
                unique_categories.append(group[0])
            else:
                # Pick the category with the most jobs
                group = sorted(
                    group, key=lambda c: Job.objects.filter(category=c).count(), reverse=True
                )
                unique_categories.append(group[0])
        # Sort alphabetically by name
        unique_categories = sorted(unique_categories, key=lambda c: c.name.lower())
        categories = [{"id": c.id, "name": c.name} for c in unique_categories]

        salary_ranges = dict(Job._meta.get_field("salary_range").choices)
        job_location_types = dict(Job._meta.get_field("job_location_type").choices)
        experience_levels = dict(Job._meta.get_field("experience_levels").choices)
        weekly_ranges = dict(Job._meta.get_field("weekly_ranges").choices)
        shifts = dict(Job._meta.get_field("shifts").choices)
        job_types = dict(Job._meta.get_field("job_type").choices)
        countries_list = [
            {
                "code": code,
                "name": name,
                "flag_url": f"https://flagcdn.com/w40/{code.lower()}.png",  # Flag URL
            }
            for code, name in countries
        ]

        return Response(
            {
                "categories": categories,
                "salary_ranges": salary_ranges,
                "job_location_types": job_location_types,
                "experience_levels": experience_levels,
                "weekly_ranges": weekly_ranges,
                "shifts": shifts,
                "job_types": job_types,
                "locations": countries_list,
            }
        )


class ExtractedSkillsAPIView(APIView):
    """
    Endpoint to fetch extracted skills for a specific job.

    Method: GET
    URL: /api/jobs/<job_id>/extracted-skills/
    Response:
    - 200 OK: Returns a list of extracted skill IDs and names.
    - 404 Not Found: If the job does not exist or the user is unauthorized.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):
        job = Job.objects.filter(id=job_id, user=request.user).first()
        if not job:
            return Response(
                {"error": "Job not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND
            )

        extracted_skills = job.extracted_skills.values("id", "name")
        return Response({"extracted_skills": list(extracted_skills)}, status=status.HTTP_200_OK)


class SearchJobsAPIView(ListAPIView):
    """
    Endpoint for advanced searching and filtering of jobs.

    Features:
    - Full-text search on job title and description.
    - Filtering by location, salary range, job type, and category.
    - Sorting by created date or salary.
    - Pagination for large result sets.
    """

    queryset = Job.objects.filter(job_creation_is_complete=True)
    serializer_class = JobSerializer
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ["title", "description"]
    filterset_fields = ["location", "salary_range", "job_type", "category"]
    ordering_fields = ["created_at", "salary"]
    pagination_class = PageNumberPagination

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        keyword = self.request.query_params.get("keyword", None)
        if keyword:
            queryset = queryset.filter(
                Q(title__icontains=keyword) | Q(description__icontains=keyword)
            )
        return queryset


class JobQuestionsAPIView(APIView):
    """
    API endpoint to fetch all questions for a job categorized by skills and submit all answers at once.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):
        """
        Fetch all questions for a job categorized by skills.

        Args:
            request: The HTTP GET request object.
            job_id: The ID of the job for which questions are being fetched.

        Returns:
            Response: A JSON response containing:
                - job_title: The title of the job.
                - total_time: Total time allocated for the quiz in seconds.
                - questions_by_skill: A dictionary where each key is a skill name, and the value is a list of questions for that skill.
        """
        user = request.user
        # Check user subscription and application limit
        subscription = Subscription.objects.filter(
            user=user, user_type="user", is_active=True
        ).first()
        if not subscription:
            return Response(
                {"message": "No active user subscription found."}, status=status.HTTP_403_FORBIDDEN
            )
        if not subscription.can_perform_action("application"):
            return Response(
                {
                    "message": "You have reached your daily job application limit for your subscription tier."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        # Example: Only allow resume enhancer for premium users
        if request.query_params.get("use_resume_enhancer") == "true":
            if not subscription.has_feature("resume_enhancer"):
                return Response(
                    {"message": "Your subscription does not include resume enhancer feature."},
                    status=status.HTTP_403_FORBIDDEN,
                )

        job = get_object_or_404(Job, id=job_id)
        skills = job.requirements.all()

        # Calculate total time allocated for the quiz
        time_per_skill = 3 * 60  # 3 minutes per skill in seconds
        total_time = skills.count() * time_per_skill

        application, _ = Application.objects.get_or_create(user=request.user, job=job)
        application.has_started = True
        application.save()

        categorized_questions = {}
        for skill in skills:
            questions = SkillQuestion.objects.filter(skill=skill, entry_level=job.level).order_by(
                "?"
            )
            categorized_questions[skill.name] = [
                {
                    "id": question.id,
                    "question": question.question,
                    "options": [
                        question.option_a,
                        question.option_b,
                        question.option_c,
                        question.option_d,
                    ],
                }
                for question in questions
            ]

        subscription.increment_usage(
            "application"
        )  # Increment usage after successful application start

        return Response(
            {
                "job_title": job.title,
                "total_time": total_time,  # Total time in seconds
                "questions_by_skill": categorized_questions,
            },
            status=200,
        )

    def post(self, request, job_id):
        """
        Submit all answers for a job at once.

        Args:
            request: The HTTP POST request object containing the user's answers.
            job_id: The ID of the job for which answers are being submitted.

        Request Body:
            {
                "responses": [
                    {
                        "question_id": <int>,
                        "answer": <str>,
                        "skill_id": <int>
                    },
                    ...
                ]
            }

        Returns:
            Response: A JSON response containing:
                - message: A success message.
                - total_score: The total score achieved by the user.
        """
        user = request.user
        job = get_object_or_404(Job, id=job_id)
        data = request.data
        responses = data.get("responses", [])

        if not responses:
            return Response({"error": "Responses are required."}, status=400)

        application, _ = Application.objects.get_or_create(user=user, job=job)
        total_score = 0

        with transaction.atomic():
            for response in responses:
                question_id = response.get("question_id")
                answer = response.get("answer")
                skill_id = response.get("skill_id")

                if not question_id or not answer or not skill_id:
                    continue

                question = get_object_or_404(SkillQuestion, id=question_id)
                skill = get_object_or_404(Skill, id=skill_id)

                # Save the applicant's answer
                applicant_answer = ApplicantAnswer.objects.create(
                    applicant=user,
                    question=question,
                    answer=answer,
                    job=job,
                    application=application,
                )
                applicant_answer.calculate_score()
                total_score += applicant_answer.score

                # Mark the skill as completed
                CompletedSkills.objects.update_or_create(
                    user=user, job=job, skill=skill, defaults={"is_completed": True}
                )

            # Update application scores
            application.quiz_score = total_score
            application.has_completed_quiz = True
            application.save()

        # Trigger top 10 update and notification logic
        update_and_notify_top10(job)
        # Notify user of quiz completion
        Notification.objects.create(
            user=user,
            notification_type=Notification.JOB_APPLICATION,
            message=f"You have completed the quiz for the job '{job.title}'.",
        )
        # Notify recruiter/company owner of new candidate quiz completion
        if job.company and job.company.user:
            Notification.objects.create(
                user=job.company.user,
                notification_type=Notification.JOB_APPLICATION,
                message=f"{user.get_full_name() or user.username} has completed the quiz for '{job.title}'.",
            )
        return Response(
            {"message": "All responses submitted successfully.", "total_score": total_score},
            status=200,
        )


class ReportTestAPIView(APIView):
    """
    API endpoint to report issues with a test for a specific job.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request, job_id):
        job = get_object_or_404(Job, id=job_id)
        reason = request.data.get("reason")

        if not reason:
            return Response({"error": "Reason is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Create a retake request
        RetakeRequest.objects.create(user=request.user, job=job, reason=reason)

        # Notify admins
        superusers = User.objects.filter(is_superuser=True)
        superuser_emails = [user.email for user in superusers]
        send_mail(
            "New Retake Request",
            f"User {request.user.username} has requested to retake the test for job {job.id}.\n\nReason:\n{reason}",
            "Assessment-Issue",
            superuser_emails,
            fail_silently=False,
        )

        return Response(
            {"message": "Retake request submitted successfully."}, status=status.HTTP_200_OK
        )


class TailoredJobDescriptionAPIView(APIView):
    """
    Generates and saves a tailored job description, responsibilities, and benefits for a job using AI.
    Expects job details and a list of required skills (not saved).
    """

    def post(self, request, job_id):
        # Subscription check: require at least standard or premium
        user = request.user
        subscription = (
            Subscription.objects.filter(user=user, user_type="recruiter", is_active=True)
            .order_by("-started_at")
            .first()
        )
        if not subscription or subscription.tier not in ["standard", "premium"]:
            return Response(
                {
                    "error": "You need a Standard or Premium recruiter subscription to use the AI job description feature. Please upgrade your plan."
                },
                status=403,
            )

        job = get_object_or_404(Job, id=job_id)
        # Extract job fields from request or use job instance as fallback
        title = request.data.get("title", job.title)
        hire_number = request.data.get("hire_number", job.hire_number)
        job_location_type = request.data.get("job_location_type", job.job_location_type)
        job_type = request.data.get("job_type", job.job_type)
        location = request.data.get("location", str(job.location))
        salary_range = request.data.get("salary_range", job.salary_range)
        category = request.data.get("category", job.category.name if job.category else "")
        experience_levels = request.data.get("experience_levels", job.experience_levels)
        weekly_ranges = request.data.get("weekly_ranges", job.weekly_ranges)
        shifts = request.data.get("shifts", job.shifts)
        skills = request.data.get("skills", [])  # List of required skills from frontend

        # randomization to the prompt for tone/style
        style_options = [
            "Use a dynamic and energetic tone that excites candidates about the opportunity.",
            "Adopt a formal and authoritative style, emphasizing professionalism and expertise.",
            "Write in a friendly, conversational manner that feels approachable and inclusive.",
            "Highlight innovation and forward-thinking, appealing to candidates who love new challenges.",
            "Focus on impact and mission, appealing to candidates who want to make a difference.",
            "Emphasize collaboration and team culture, making the role attractive to team players.",
        ]
        chosen_style = random.choice(style_options)

        prompt = (
            "YOU ARE A WORLD-CLASS HR COPYWRITER AND TALENT ACQUISITION SPECIALIST. "
            "YOUR TASK IS TO CREATE THE MOST EFFECTIVE, ENGAGING, AND ATS-OPTIMIZED JOB DESCRIPTION, RESPONSIBILITIES, AND BENEFITS FOR THE ROLE BELOW. "
            "YOUR OUTPUT WILL BE USED IN A REAL JOB POSTING TO ATTRACT TOP TALENT AND ENSURE HIGH RELEVANCY FOR BOTH HUMAN RECRUITERS AND APPLICANT TRACKING SYSTEMS (ATS).\n\n"
            f"###STYLE###\n{chosen_style}\n\n"
            "###INSTRUCTIONS###\n"
            "- Analyze all provided job details and required skills.\n"
            "- The experience level (e.g., 5-10 years) is a mandatory requirement and must be clearly stated in the job description and responsibilities.\n"
            "- Write a compelling, clear, and concise job description that highlights the impact, mission, unique aspects of the role and company, and explicitly states the required years of experience.\n"
            "- Responsibilities should be actionable, specific, and results-oriented, using bullet points and strong verbs. At least one bullet should reference the required experience level.\n"
            "- Benefits should be attractive, concrete, and reflect both tangible (salary, insurance, perks) and intangible (growth, culture, flexibility) aspects.\n"
            "- Integrate relevant keywords, skills, and tools from the provided skills list and job context.\n"
            "- Use inclusive, bias-free, and motivating language.\n"
            "- Format output as a valid JSON object with three fields: description, responsibilities, benefits. Each field should be a string (responsibilities as a bullet list in a string).\n"
            "- Do NOT include any extra text, explanations, or sections outside of description, responsibilities, and benefits.\n"
            "- Ensure the writing is ATS-friendly: no graphics, tables, or unusual formatting.\n"
            "- Make sure the description is unique, not generic, and tailored to the provided details.\n\n"
            "###JOB DETAILS###\n"
            f"Job Title: {title}\n"
            f"Hire Number: {hire_number}\n"
            f"Job Location Type: {job_location_type}\n"
            f"Job Type: {job_type}\n"
            f"Location: {location}\n"
            f"Salary Range: {salary_range}\n"
            f"Category: {category}\n"
            f"Experience Levels: {experience_levels}\n"
            f"Weekly Ranges: {weekly_ranges}\n"
            f"Shifts: {shifts}\n"
            f"Required Skills: {', '.join(skills)}\n\n"
            "###EXAMPLES###\n"
            "description: \"Join our mission-driven team as a Senior Data Scientist (5+ years experience required), where you'll build scalable solutions impacting thousands of users. You'll collaborate with cross-functional teams, leverage modern technologies, and contribute to a culture of innovation and excellence.\"\n"
            'responsibilities: "- Design, develop, and deploy high-quality software solutions\n'
            "- Collaborate with product managers and designers to define requirements\n"
            "- Implement best practices for code quality, testing, and documentation\n"
            "- Mentor junior engineers and contribute to team knowledge sharing\n"
            "- Leverage at least 5 years of experience in data science to drive impactful projects\n"
            '- Continuously improve system performance and scalability"\n'
            'benefits: "- Competitive salary and performance bonuses\n'
            "- Comprehensive health, dental, and vision insurance\n"
            "- Flexible remote work options\n"
            "- Professional development budget\n"
            '- Inclusive and collaborative team culture"\n'
            "###END###\n"
        )

        # Call OpenAI API
        try:
            openai.api_key = getattr(settings, "OPENAI_API_KEY", None)
            client = openai.OpenAI(api_key=openai.api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=1000,
                temperature=0.7,
            )
            ai_content = response.choices[0].message.content

            # Clean up control characters and invalid JSON before parsing
            ai_content_clean = re.sub(r"[\x00-\x1F\x7F]", "", ai_content)
            # Optionally, try to extract the first JSON object if extra text is present
            match = re.search(r"\{.*\}", ai_content_clean, re.DOTALL)
            if match:
                ai_content_clean = match.group(0)

            result = json.loads(ai_content_clean)
        except Exception as e:
            return Response({"error": f"AI generation failed: {str(e)}"}, status=500)

        # Save to job fields
        try:
            job.description = result.get("description", job.description)
            job.responsibilities = result.get("responsibilities", job.responsibilities)
            job.benefits = result.get("benefits", job.benefits)
            job.save()
        except Exception as e:
            return Response(
                {"error": f"Failed to save tailored job description: {str(e)}"}, status=500
            )

        return Response(
            {
                "message": "Tailored job description generated and saved successfully.",
                "description": job.description,
                "responsibilities": job.responsibilities,
                "benefits": job.benefits,
            },
            status=200,
        )


class UpdateJobStep1APIView(APIView):
    """
    Endpoint to update the first step of an existing job (basic details).

    This step includes:
    - Title
    - Hire number
    - Job location type
    - Job type
    - Location
    - Salary range
    - Category

    Method: PATCH
    URL: /api/jobs/<job_id>/update-step1/
    Request Body:
    {
        "title": "Senior Software Engineer",
        "hire_number": 5,
        "job_location_type": "hybrid",
        "job_type": "Full_time",
        "location": "CA",
        "salary_range": "100001-150000",
        "category": 2
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
            return Response(
                {"error": "Job not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND
            )

        data = {
            "title": request.data.get("title"),
            "hire_number": request.data.get("hire_number"),
            "job_location_type": request.data.get("job_location_type"),
            "job_type": request.data.get("job_type"),
            "location": request.data.get("location"),
            "salary_range": request.data.get("salary_range"),
            "category": request.data.get("category"),
        }
        
        # Remove None values to only update provided fields
        data = {k: v for k, v in data.items() if v is not None}
        
        serializer = JobSerializer(job, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "job": serializer.data,
                    "message": "Job basic details updated successfully."
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateJobStep2APIView(APIView):
    """
    Endpoint to update the second step of an existing job (preferences).

    This step includes:
    - Job type
    - Experience levels
    - Weekly ranges
    - Shifts

    Method: PATCH
    URL: /api/jobs/<job_id>/update-step2/
    Request Body:
    {
        "job_type": "Full_time",
        "experience_levels": "3-5Years",
        "weekly_ranges": "mondayToFriday",
        "shifts": "dayShift"
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
            return Response(
                {"error": "Job not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND
            )

        data = {
            "job_type": request.data.get("job_type"),
            "experience_levels": request.data.get("experience_levels"),
            "weekly_ranges": request.data.get("weekly_ranges"),
            "shifts": request.data.get("shifts"),
        }
        
        # Remove None values to only update provided fields
        data = {k: v for k, v in data.items() if v is not None}
        
        serializer = JobSerializer(job, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "job": serializer.data,
                    "message": "Job preferences updated successfully."
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateJobStep3APIView(APIView):
    """
    Endpoint to update the third step of an existing job (description and content).

    This step includes:
    - Description
    - Responsibilities
    - Benefits

    Note: This endpoint does NOT extract technical skills or call ChatGPT.
    Skills extraction is only done during the initial job creation process.

    Method: PATCH
    URL: /api/jobs/<job_id>/update-step3/
    Request Body:
    {
        "description": "We are seeking an experienced software engineer...",
        "responsibilities": "Lead development of web applications...",
        "benefits": "Competitive salary, health benefits, remote work..."
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
            return Response(
                {"error": "Job not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND
            )

        data = {
            "description": request.data.get("description"),
            "responsibilities": request.data.get("responsibilities"),
            "benefits": request.data.get("benefits"),
        }
        
        # Remove None values to only update provided fields
        data = {k: v for k, v in data.items() if v is not None}
        
        serializer = JobSerializer(job, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            
            # No skill extraction during updates - only return the updated job
            return Response(
                {
                    "job": serializer.data,
                    "message": "Job description updated successfully."
                },
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UpdateJobStep4APIView(APIView):
    """
    Endpoint to update the fourth step of an existing job (requirements and level).

    This step includes:
    - Requirements (skills selected from previously extracted skills)
    - Level (skill level)

    Note: This endpoint does NOT generate new questions or call ChatGPT.
    Question generation is only done during the initial job creation process.

    Method: PATCH
    URL: /api/jobs/<job_id>/update-step4/
    Request Body:
    {
        "requirements": [1, 2, 3],
        "level": "Expert"
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
            return Response(
                {"error": "Job not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND
            )

        # Extract requirements and level from the request
        requirements = request.data.get("requirements")
        level = request.data.get("level")

        # Update requirements if provided
        if requirements is not None:
            try:
                skills = Skill.objects.filter(id__in=requirements)
                if len(skills) != len(requirements):
                    return Response(
                        {"error": "One or more skill IDs are invalid."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                job.requirements.set(skills)
            except Exception as e:
                return Response(
                    {"error": f"Error validating skills: {str(e)}"}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        # Update level if provided
        if level is not None:
            job.level = level

        job.save()

        # Create notification for job update
        Notification.objects.create(
            user=request.user,
            notification_type=Notification.NEW_JOB_POSTED,
            message=f"Your job '{job.title}' has been updated successfully.",
        )

        # No question generation during updates - only return the updated job
        return Response(
            {
                "job": JobSerializer(job).data,
                "message": "Job requirements updated successfully."
            },
            status=status.HTTP_200_OK
        )


class UpdateJobAvailabilityAPIView(APIView):
    """
    Endpoint to toggle job availability (publish/unpublish).

    Method: PATCH
    URL: /api/jobs/<job_id>/toggle-availability/
    Request Body:
    {
        "is_available": true
    }
    Response:
    - 200 OK: Returns the updated job availability status.
    - 404 Not Found: If the job does not exist or the user is unauthorized.
    """

    permission_classes = [IsAuthenticated]

    def patch(self, request, job_id):
        job = Job.objects.filter(id=job_id, user=request.user).first()
        if not job:
            return Response(
                {"error": "Job not found or unauthorized."}, status=status.HTTP_404_NOT_FOUND
            )

        is_available = request.data.get("is_available")
        if is_available is None:
            return Response(
                {"error": "is_available field is required."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        job.is_available = is_available
        job.save()

        status_text = "published" if is_available else "unpublished"
        
        # Create notification
        Notification.objects.create(
            user=request.user,
            notification_type=Notification.NEW_JOB_POSTED,
            message=f"Your job '{job.title}' has been {status_text}.",
        )

        return Response(
            {
                "job_id": job.id,
                "title": job.title,
                "is_available": job.is_available,
                "message": f"Job has been {status_text} successfully."
            },
            status=status.HTTP_200_OK
        )


class RecruiterJobListAPIView(ListAPIView):
    """
    Endpoint to list all jobs created by the authenticated recruiter.

    Method: GET
    URL: /api/jobs/my-jobs/
    Response:
    - 200 OK: Returns a list of jobs created by the recruiter.
    """

    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Short-circuit for Swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Job.objects.none()
        return Job.objects.filter(user=self.request.user).order_by('-created_at')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class RecruiterJobDetailAPIView(RetrieveAPIView):
    """
    Endpoint to get detailed information about a specific job created by the recruiter.

    Method: GET
    URL: /api/jobs/my-jobs/<job_id>/
    Response:
    - 200 OK: Returns detailed job information.
    - 404 Not Found: If the job does not exist or the user is unauthorized.
    """

    serializer_class = JobSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Short-circuit for Swagger schema generation
        if getattr(self, 'swagger_fake_view', False):
            return Job.objects.none()
        return Job.objects.filter(user=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class JobCreationProgressAPIView(APIView):
    """
    Endpoint to check the progress of job creation, specifically question generation.
    
    Method: GET
    URL: /api/jobs/<job_id>/creation-progress/
    Response:
    {
        "job_id": 123,
        "is_complete": false,
        "progress": {
            "total_skills": 3,
            "completed_skills": 1,
            "percentage": 33.33,
            "skills_status": {
                "Python": true,
                "JavaScript": false,
                "React": false
            }
        }
    }
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, job_id):
        job = Job.objects.filter(id=job_id, user=request.user).first()
        if not job:
            return Response(
                {"error": "Job not found or unauthorized."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        # Get all required skills
        skills = job.requirements.all()
        total_skills = skills.count()
        
        if total_skills == 0:
            return Response({
                "job_id": job.id,
                "is_complete": job.job_creation_is_complete,
                "progress": {
                    "total_skills": 0,
                    "completed_skills": 0,
                    "percentage": 100,
                    "skills_status": {}
                }
            })

        # Get detailed status for each skill
        from job.models import SkillGenerationStatus
        skill_statuses = SkillGenerationStatus.objects.filter(job=job)
        status_map = {s.skill_id: s for s in skill_statuses}
        
        completed_skills = 0
        skills_status = {}
        
        for skill in skills:
            status_obj = status_map.get(skill.id)
            if status_obj:
                is_complete = status_obj.status in ['ai_success', 'fallback_used', 'skipped']
                skills_status[skill.name] = {
                    "complete": is_complete,
                    "status": status_obj.status,
                    "questions_count": status_obj.questions_generated,
                    "ai_attempts": status_obj.ai_attempts,
                    "source": status_obj.status
                }
                if is_complete:
                    completed_skills += 1
            else:
                skills_status[skill.name] = {
                    "complete": False,
                    "status": "pending",
                    "questions_count": 0,
                    "ai_attempts": 0,
                    "source": "pending"
                }

        percentage = (completed_skills / total_skills) * 100

        return Response({
            "job_id": job.id,
            "is_complete": job.job_creation_is_complete,
            "progress": {
                "total_skills": total_skills,
                "completed_skills": completed_skills,
                "percentage": round(percentage, 2),
                "skills_status": skills_status
            }
        })
