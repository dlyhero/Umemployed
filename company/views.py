import json
import logging
import random
import string

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Count
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta

from job.models import Application, Job, Rating
from resume.models import ContactInfo, Resume, ResumeDoc, UserLanguage, UserProfile, WorkExperience
from resume.views import calculate_skill_match
from users.models import User

from .decorators import company_belongs_to_user
from .forms import CreateCompanyForm, RatingForm, UpdateCompanyForm
from .models import Company, Interview, GoogleCredentials
from .google_utils import GoogleCalendarManager, credentials_to_dict, credentials_from_dict

# Configure logging
logger = logging.getLogger(__name__)


@login_required(login_url="login")
@company_belongs_to_user
def company_details(request, company_id):
    company = Company.objects.get(id=company_id)
    context = {
        "company": company,
    }
    return render(request, "company/companyInfo.html", context)


# create company
@login_required(login_url="login")
def create_company(request):
    print("entered create company")
    try:
        company = request.user.company
        messages.warning(request, "Permission Denied! You have already created a company.")
        return redirect("switch_account")
    except Company.DoesNotExist:
        if request.method == "POST":
            print(request.POST)
            form = CreateCompanyForm(request.POST, request.FILES)  # Make sure to add request.FILES
            if form.is_valid():
                company = form.save(commit=False)
                company.user = request.user
                company.save()
                request.user.is_applicant = False
                request.user.has_company = True
                request.user.is_recruiter = True
                request.user.has_resume = True
                request.user.save()
                messages.success(request, "Company created successfully.")
                # Redirect to company_details with the newly created company's ID
                return redirect("update_company", company_id=company.id)
            else:
                print(form.errors)  # This will print out form errors to the console
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
        else:
            form = CreateCompanyForm()

        context = {"form": form}
        return render(request, "company/create_company.html", context)


@login_required(login_url="login")
@company_belongs_to_user
def update_company(request, company_id):
    company = get_object_or_404(Company, id=company_id, user=request.user)
    logger.debug(f"User {request.user} is updating company {company.name}")

    # Check if the logged-in user is a recruiter
    if request.user.is_recruiter:
        if request.method == "POST":
            # Handle file uploads with request.FILES
            form = UpdateCompanyForm(request.POST, request.FILES, instance=company)
            logger.debug("Form data received: %s", request.POST)
            form.instance.user = request.user

            if form.is_valid():
                form.save()
                # Update user's has_company status after form submission
                request.user.has_company = True
                request.user.save()
                logger.debug(
                    "Company information updated successfully for company: %s", company.name
                )

                # Display a success message and redirect to 'view_my_jobs'
                messages.success(request, "Your company information has been updated successfully.")
                return redirect("company_dashboard", company.id)
            else:
                # Log form errors
                logger.warning("Form errors: %s", form.errors)
                # Display a warning if form submission fails
                messages.warning(
                    request,
                    "There was an issue with the form. Please correct the errors and try again.",
                )
        else:
            # If not a POST request, render the form with the existing company instance
            form = UpdateCompanyForm(instance=company)
            logger.debug("Rendering form with existing company instance: %s", company.name)

        # Pass the form and company to the context
        context = {"form": form, "company": company}
        return render(request, "company/update_company.html", context)

    # Deny permission if the user is not a recruiter
    else:
        logger.warning("Permission Denied: User %s tried to access update_company", request.user)
        messages.warning(
            request, "Permission Denied. You don't have access to update company information."
        )
        return redirect("user_dashboard")


@login_required(login_url="login")
@company_belongs_to_user
def company_dashboard(request, company_id):
    company = get_object_or_404(Company, id=company_id)

    jobs = Job.objects.filter(company=company).order_by(
        "-created_at"
    )  # Assuming `created_at` is your timestamp field

    # Add the number of applications to each job
    for job in jobs:
        job.application_count = Application.objects.filter(job=job).count()

    context = {
        "company": company,
        "jobs": jobs,  # Pass the jobs to the template
    }

    return render(request, "company/dashboard.html", context)


@login_required(login_url="login")
@company_belongs_to_user
def view_my_jobs(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    jobs = Job.objects.filter(company=company).order_by("-created_at")

    for job in jobs:
        job.application_count = Application.objects.filter(job=job).count()

    context = {
        "company": company,
        "jobs": jobs,
    }
    return render(request, "company/myJobs.html", context)


@login_required(login_url="login")
@company_belongs_to_user
def view_applications(request, company_id):
    # Check if the current user is the owner of the company
    applications = []
    current_user = request.user
    company = Company.objects.get(id=company_id)
    if company.user != current_user:
        return HttpResponse("You are not authorized to view this page.")

    jobs = Job.objects.filter(company=company)
    job_applications = {}
    for job in jobs:
        applications = Application.objects.filter(job=job)
        job_applications[job] = applications

    # Calculate match percentage for each application
    for job, applications in job_applications.items():
        for application in applications:
            user = application.user
            resume = Resume.objects.filter(
                user=user
            ).first()  # Use filter() to avoid DoesNotExist error

            if resume:  # Check if the user has a resume
                applicant_skills = set(resume.skills.all())
                job_skills = set(job.requirements.all())
                match_percentage, missing_skills = calculate_skill_match(
                    applicant_skills, job_skills
                )
                application.matching_percentage = match_percentage

                # Calculate the quiz score (assumed to be stored in application.quiz_score)
                quiz_score = application.quiz_score

                # Calculate the overall score using match percentage and quiz score
                overall_score = match_percentage * 0.7 + (quiz_score / 10) * 0.3
                # Optionally, you can load user qualifications and skills for rendering in template
                application.user.skills_list = list(
                    resume.skills.all()
                )  # Create a separate attribute
                application.user.resume = resume
            else:
                # Handle cases where no resume exists (optional: set default values)
                application.matching_percentage = 0
                application.overall_score = application.quiz_score / 10 * 0.3  # Only quiz score
                application.user.skills_list = []
        job_applications[job] = applications

    context = {
        "company": company,
        "job_applications": job_applications,
        "applications": applications,
    }
    return render(request, "company/candidates.html", context)


def application_details(request, application_id):
    # Retrieve the application object
    application = get_object_or_404(Application, id=application_id)
    user = application.user

    print(f"Debug: Application ID: {application_id}")  # Debugging output
    print(f"Debug: User ID: {user.id}, User Email: {user.email}")  # Debugging output

    # Get resume and associated documents
    resume = Resume.objects.filter(user=user).first()
    resume_doc = ResumeDoc.objects.filter(user=user).first()  # Get the associated ResumeDoc
    contact_info = ContactInfo.objects.filter(user=user).first()
    profile = UserProfile.objects.filter(user=user).first()

    print(
        f"Debug: Resume: {resume}, Resume Doc: {resume_doc}, Contact Info: {contact_info}, Profile: {profile}"
    )  # Debugging output

    # Get work experiences related to the user
    work_experiences = WorkExperience.objects.filter(user=user).values(
        "company_name", "role", "start_date", "end_date"
    )

    print(f"Debug: Work Experiences: {list(work_experiences)}")  # Debugging output

    # Get languages associated with the user's profile
    languages = UserLanguage.objects.filter(user_profile=profile).values("language__name")

    print(f"Debug: Languages: {list(languages)}")  # Debugging output

    data = {
        "first_name": resume.first_name if resume else user.first_name,
        "surname": resume.surname if resume else user.last_name,
        "state": resume.state if resume else None,
        "country": resume.country if resume else (profile.country if profile else None),
        "job_title": resume.job_title if resume else "No job title found",
        "date_of_birth": resume.date_of_birth if resume else "Date of birth not provided",
        "phone": resume.phone
        if resume
        else (contact_info.phone if contact_info else "Phone not provided"),
        "description": resume.description if resume else "No description available",
        "profile_image": resume.profile_image.url
        if resume and resume.profile_image
        else "No image available",
        "cv": resume.cv.url if resume and resume.cv else "No CV uploaded",
        "skills": list(resume.skills.values_list("name", flat=True)) if resume else [],
        "email": contact_info.email if contact_info else user.email,
        "resume_pdf": resume_doc.file.url
        if resume_doc and resume_doc.file
        else "No resume PDF available",
        "work_experiences": list(work_experiences),  # Include work experiences
        "languages": list(languages),  # Include languages
    }

    print(f"Debug: Final Data: {data}")  # Debugging output before returning

    return JsonResponse(data)


def job_applications_view(request, company_id, job_id):
    current_user = request.user
    # Check if the company exists and if the current user is the owner
    company = get_object_or_404(Company, id=company_id)
    if company.user != current_user:
        return HttpResponse("You are not authorized to view this page.")

    # Get the specific job belonging to the company
    job = get_object_or_404(Job, id=job_id, company=company)

    # Query applications for the specific job
    applications = Application.objects.filter(job=job)

    # Calculate match percentage and overall score for each application
    for application in applications:
        user = application.user
        resume = Resume.objects.filter(user=user).first()  # Avoid DoesNotExist error

        if resume:  # Check if the user has a resume
            applicant_skills = set(resume.skills.all())
            job_skills = set(job.requirements.all())
            match_percentage, missing_skills = calculate_skill_match(applicant_skills, job_skills)
            application.matching_percentage = match_percentage

            # Calculate the quiz score (assumed to be stored in application.quiz_score)
            quiz_score = application.quiz_score

            # Calculate the overall score using match percentage and quiz score
            overall_score = match_percentage * 0.7 + (quiz_score / 10) * 0.3
            application.overall_score = overall_score

            # Load user qualifications and skills for rendering in template
            application.user.skills_list = list(
                resume.skills.all()
            )  # Add skills to user for rendering
            application.user.resume = resume
        else:
            # Handle cases where no resume exists
            application.matching_percentage = 0
            application.overall_score = application.quiz_score / 10 * 0.3  # Only quiz score
            application.user.skills_list = []

    # Sort applications based on quiz score, matching percentage, and randomly if there's a tie
    applications = sorted(
        applications,
        key=lambda x: (x.quiz_score, x.matching_percentage, random.random()),
        reverse=True,
    )

    # Select top 5 applications and the next 5 for the waiting list
    top_5_applications = applications[:5]
    waiting_list_applications = applications[5:10]

    context = {
        "company": company,
        "job": job,
        "top_5_applications": top_5_applications,
        "waiting_list_applications": waiting_list_applications,
    }
    return render(request, "company/job_applications.html", context)


@login_required(login_url="login")
@company_belongs_to_user
def view_application_details(request, application_id, company_id):
    application = get_object_or_404(Application, id=application_id)
    current_user = request.user
    company = Company.objects.get(id=company_id)
    if company.user != current_user:
        return HttpResponse("You are not authorized to view this page.")

    jobs = Job.objects.filter(company=company)
    job_applications = {}
    for job in jobs:
        applications = Application.objects.filter(job=job)
        job_applications[job] = applications

    context = {
        "application": application,
        "company": company,
    }
    return render(request, "company/application_details.html", context)


@login_required(login_url="login")
@company_belongs_to_user
def company_analytics(request, company_id):
    company = Company.objects.get(id=company_id)
    current_user = request.user
    if company.user != current_user:
        return HttpResponse("You are not authorized to view this page.")

    return render(request, "company/analytics.html")


def company_inbox(request, company_id):
    company = Company.objects.get(id=company_id)
    current_user = request.user
    if company.user != current_user:
        return HttpResponse("You are not authorized to view this page.")

    return render(request, "company/inbox.html", {"company": company})


def company_notifications(request, company_id):
    company = Company.objects.get(id=company_id)
    current_user = request.user
    if company.user != current_user:
        return HttpResponse("You are not authorized to view this page.")

    return render(request, "company/notifications.html", {"company": company})


def company_detail_view(request, pk):
    company = get_object_or_404(Company, pk=pk)
    jobs = Job.objects.filter(company=company)
    is_owner = request.user == company.user
    applied_job_ids = []

    # Check if the user is authenticated before querying applications
    if request.user.is_authenticated:
        applied_job_ids = Application.objects.filter(user=request.user).values_list(
            "job_id", flat=True
        )
    return render(
        request,
        "company/company_detail.html",
        {
            "company": company,
            "jobs": jobs,
            "applied_job_ids": applied_job_ids,
            "is_owner": is_owner,
        },
    )


def company_jobs_list_view(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    jobs = Job.objects.filter(company=company)

    return render(request, "company/company_jobs_list.html", {"company": company, "jobs": jobs})


def company_list_view(request):
    companies = Company.objects.annotate(available_jobs=Count("job"))

    # Pagination logic
    page = request.GET.get("page", 1)
    paginator = Paginator(companies, 3)  # Show 3 companies per page
    try:
        companies = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver the first page.
        companies = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g., less than 1 or greater than max pages), deliver the first page.
        companies = paginator.page(1)

    return render(request, "company/company_list.html", {"companies": companies})


def generate_meeting_link():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=8))


def create_interview(request):
    if request.method == "POST":
        candidate_id = request.POST.get("candidate_id")
        job_title = request.POST.get("job_title")
        date = request.POST.get("date")
        time = request.POST.get("time")
        timezone = request.POST.get("timezone")
        note = request.POST.get("note")

        candidate = User.objects.get(id=candidate_id)
        recruiter = request.user

        # Assuming job_title is unique and can be used to retrieve the job instance
        job = Job.objects.get(title=job_title)
        company_name = job.company.name  # Assuming the Company model has a 'name' field

        # Create the interview instance to get the room_id
        interview = Interview.objects.create(
            candidate=candidate, date=date, time=time, timezone=timezone, note=note
        )

        # Generate the meeting link using the room_id
        current_site = get_current_site(request)
        base_url = f"http://{current_site.domain}"
        meeting_link = f"{base_url}/chat/"
        room_id = interview.room_id
        interview.meeting_link = meeting_link
        interview.save()

        # Render email templates
        candidate_email_content = render_to_string(
            "emails/candidate_interview_email.html",
            {
                "candidate": candidate,
                "job_title": job_title,
                "date": date,
                "time": time,
                "timezone": timezone,
                "meeting_link": meeting_link,
                "room_id": room_id,
                "note": note,
                "company_name": company_name,
            },
        )

        recruiter_email_content = render_to_string(
            "emails/recruiter_interview_email.html",
            {
                "recruiter": recruiter,
                "candidate": candidate,
                "job_title": job_title,
                "date": date,
                "time": time,
                "timezone": timezone,
                "meeting_link": meeting_link,
                "room_id": room_id,
                "note": note,
                "company_name": company_name,
            },
        )

        # Send email to candidate
        send_mail(
            "Interview Scheduled",
            candidate_email_content,
            "from@example.com",
            [candidate.email],
            fail_silently=False,
            html_message=candidate_email_content,
        )

        # Send email to recruiter
        send_mail(
            "Interview Scheduled",
            recruiter_email_content,
            "from@example.com",
            [recruiter.email],
            fail_silently=False,
            html_message=recruiter_email_content,
        )

        return JsonResponse({"message": "Interview created successfully."})

    return JsonResponse({"error": "Invalid request method."}, status=400)


from django.http import HttpResponseForbidden

from resume.models import WorkExperience


@login_required(login_url="login")
def rate_candidate(request, candidate_id):
    candidate = get_object_or_404(User, id=candidate_id)
    endorser = request.user

    # Ensure the endorser and candidate have a past relationship in a company or matching email domains
    candidate_companies = WorkExperience.objects.filter(user=candidate).values_list(
        "company_name", flat=True
    )
    endorser_companies = WorkExperience.objects.filter(user=endorser).values_list(
        "company_name", flat=True
    )
    candidate_email_domain = candidate.email.split("@")[-1]
    endorser_email_domain = endorser.email.split("@")[-1]

    if not (
        set(candidate_companies).intersection(set(endorser_companies))
        or candidate_email_domain == endorser_email_domain
    ):
        return HttpResponseForbidden("You are not allowed to rate this candidate.")

    # Check if a rating already exists
    rating = Rating.objects.filter(candidate=candidate, endorser=endorser).first()

    if request.method == "POST":
        form = RatingForm(request.POST, instance=rating)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.candidate = candidate
            rating.endorser = endorser
            rating.save()
            return redirect("home")  # Redirect to a success page or the candidate's profile
    else:
        form = RatingForm(instance=rating)

    context = {
        "form": form,
        "candidate": candidate,
    }
    return render(request, "reviews/rate_candidate.html", context)


@login_required(login_url="login")
def company_related_users(request):
    current_user = request.user
    user_companies = WorkExperience.objects.filter(user=current_user).values_list(
        "company_name", flat=True
    )
    current_user_email_domain = current_user.email.split("@")[-1]

    related_users = (
        User.objects.filter(work_experiences__company_name__in=user_companies)
        .distinct()
        .exclude(id=current_user.id)
    )

    # Include users with matching email domains
    related_users_by_email = (
        User.objects.filter(email__endswith=current_user_email_domain)
        .distinct()
        .exclude(id=current_user.id)
    )

    # Combine both querysets
    related_users = related_users | related_users_by_email

    context = {
        "related_users": related_users.distinct(),
    }
    return render(request, "company/related_users.html", context)


from transactions.models import Transaction
from users.models import User


# view related to recruiter starting to view applicants endorsements
@login_required(login_url="login")
def start_payment_for_endorsement(request, candidate_id):
    candidate = get_object_or_404(User, id=candidate_id)

    # Check if the user has a completed transaction for this candidate
    has_paid = Transaction.objects.filter(
        user=request.user, candidate=candidate, status="completed"
    ).exists()

    if has_paid:
        # Redirect to the endorsements page if the user has already paid
        return redirect("candidate_endorsements", candidate_id=candidate_id)

    # Store the candidate ID in the session
    request.session["candidate_id"] = candidate_id
    return render(request, "company/payments/start_payment.html", {"candidate": candidate})


# Google Meet Integration Views

@login_required(login_url="login")
def google_connect(request):
    """Start Google OAuth flow for calendar access"""
    redirect_uri = request.build_absolute_uri(reverse('google_oauth_callback'))
    authorization_url, state = GoogleCalendarManager.get_authorization_url(request, redirect_uri)
    request.session['oauth_state'] = state
    return redirect(authorization_url)


@login_required(login_url="login")
def google_oauth_callback(request):
    """Handle Google OAuth callback and store credentials"""
    try:
        state = request.session.get('oauth_state')
        if not state:
            messages.error(request, "OAuth state not found. Please try again.")
            return redirect('company_dashboard')
        
        redirect_uri = request.build_absolute_uri(reverse('google_oauth_callback'))
        authorization_response = request.build_absolute_uri()
        
        credentials = GoogleCalendarManager.exchange_code_for_tokens(
            authorization_response, state, redirect_uri
        )
        
        # Store credentials in database
        google_creds, created = GoogleCredentials.objects.get_or_create(
            user=request.user,
            defaults={'credentials_json': json.dumps(credentials_to_dict(credentials))}
        )
        
        if not created:
            google_creds.credentials_json = json.dumps(credentials_to_dict(credentials))
            google_creds.save()
        
        messages.success(request, "Google Calendar connected successfully! You can now schedule Google Meet interviews.")
        
        # Clean up session
        if 'oauth_state' in request.session:
            del request.session['oauth_state']
        
        # Redirect to where user was trying to go
        next_url = request.session.get('google_connect_next', 'company_dashboard')
        if 'google_connect_next' in request.session:
            del request.session['google_connect_next']
        
        return redirect(next_url)
        
    except Exception as e:
        messages.error(request, f"Error connecting to Google: {str(e)}")
        return redirect('company_dashboard')


@login_required(login_url="login")
def check_google_connection(request):
    """API endpoint to check if user has Google Calendar connected"""
    try:
        google_creds = GoogleCredentials.objects.get(user=request.user)
        return JsonResponse({'connected': True})
    except GoogleCredentials.DoesNotExist:
        return JsonResponse({'connected': False})


def create_google_meet_interview(request):
    """Create an interview with Google Meet link"""
    if request.method == "POST":
        try:
            candidate_id = request.POST.get("candidate_id")
            job_title = request.POST.get("job_title")
            date_str = request.POST.get("date")
            time_str = request.POST.get("time")
            timezone_str = request.POST.get("timezone", "UTC")
            note = request.POST.get("note", "")

            candidate = User.objects.get(id=candidate_id)
            recruiter = request.user

            # Check if recruiter has Google credentials
            try:
                google_creds = GoogleCredentials.objects.get(user=recruiter)
                credentials_dict = json.loads(google_creds.credentials_json)
                credentials = credentials_from_dict(credentials_dict)
            except GoogleCredentials.DoesNotExist:
                return JsonResponse({
                    "error": "Google Calendar not connected",
                    "needs_google_auth": True,
                    "connect_url": reverse('google_connect')
                }, status=400)

            # Parse date and time
            interview_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            interview_time = datetime.strptime(time_str, "%H:%M").time()
            
            # Combine date and time
            interview_datetime = datetime.combine(interview_date, interview_time)
            # Add timezone awareness if needed
            interview_datetime = timezone.make_aware(interview_datetime, timezone.get_current_timezone())
            
            # Set end time (1 hour later)
            end_datetime = interview_datetime + timedelta(hours=1)

            # Get job info
            job = Job.objects.get(title=job_title)
            company_name = job.company.name

            # Create Google Calendar event
            calendar_manager = GoogleCalendarManager(credentials)
            
            event_summary = f"Interview: {job_title} - {candidate.get_full_name()}"
            event_description = f"""
Interview for position: {job_title}
Company: {company_name}
Candidate: {candidate.get_full_name()} ({candidate.email})
Recruiter: {recruiter.get_full_name()} ({recruiter.email})

Notes: {note}
            """.strip()
            
            attendees = [candidate.email, recruiter.email]
            
            # Create the event
            event = calendar_manager.create_meet_event(
                summary=event_summary,
                start_datetime=interview_datetime,
                end_datetime=end_datetime,
                attendees_emails=attendees,
                description=event_description
            )
            
            # Extract Google Meet link
            meet_link = event.get('conferenceData', {}).get('entryPoints', [{}])[0].get('uri', '')
            
            # Create interview record
            interview = Interview.objects.create(
                candidate=candidate,
                recruiter=recruiter,
                interview_type='google_meet',
                date=interview_date,
                time=interview_time,
                timezone=timezone_str,
                meeting_link=meet_link,
                google_event_id=event['id'],
                note=note
            )

            # Send email notifications
            send_google_meet_emails(interview, job, company_name)

            return JsonResponse({
                "message": "Google Meet interview created successfully.",
                "meet_link": meet_link,
                "event_id": event['id']
            })

        except Exception as e:
            return JsonResponse({"error": f"Failed to create Google Meet interview: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request method."}, status=400)


def send_google_meet_emails(interview, job, company_name):
    """Send email notifications for Google Meet interview"""
    candidate = interview.candidate
    recruiter = interview.recruiter
    
    # Render email templates
    candidate_email_content = render_to_string(
        "emails/candidate_google_meet_interview_email.html",
        {
            "candidate": candidate,
            "job_title": job.title,
            "date": interview.date,
            "time": interview.time,
            "timezone": interview.timezone,
            "meeting_link": interview.meeting_link,
            "note": interview.note,
            "company_name": company_name,
            "recruiter": recruiter,
        },
    )

    recruiter_email_content = render_to_string(
        "emails/recruiter_google_meet_interview_email.html",
        {
            "recruiter": recruiter,
            "candidate": candidate,
            "job_title": job.title,
            "date": interview.date,
            "time": interview.time,
            "timezone": interview.timezone,
            "meeting_link": interview.meeting_link,
            "note": interview.note,
            "company_name": company_name,
        },
    )

    # Send emails
    try:
        send_mail(
            "Google Meet Interview Scheduled",
            candidate_email_content,
            "from@example.com",
            [candidate.email],
            fail_silently=False,
            html_message=candidate_email_content,
        )

        send_mail(
            "Google Meet Interview Scheduled",
            recruiter_email_content,
            "from@example.com",
            [recruiter.email],
            fail_silently=False,
            html_message=recruiter_email_content,
        )
    except Exception as e:
        logger.error(f"Failed to send interview emails: {str(e)}")


@login_required(login_url="login")
def disconnect_google(request):
    """Disconnect Google Calendar integration"""
    try:
        google_creds = GoogleCredentials.objects.get(user=request.user)
        google_creds.delete()
        messages.success(request, "Google Calendar disconnected successfully.")
    except GoogleCredentials.DoesNotExist:
        messages.info(request, "Google Calendar was not connected.")
    
    return redirect('company_dashboard')
