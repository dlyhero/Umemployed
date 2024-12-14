from django.shortcuts import get_object_or_404, redirect, render

from django.contrib import messages
from .models import Company
from users.models import User
from .forms import UpdateCompanyForm, CreateCompanyForm
from django.contrib.auth.decorators import login_required
from .decorators import company_belongs_to_user

from resume.views import calculate_skill_match

from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from job.models import Job, Application
from resume.models import Resume
from .forms import UpdateCompanyForm
from .models import Company
import random
import logging
from resume.models import  Resume,ContactInfo, UserProfile, ResumeDoc, WorkExperience, UserLanguage
from job.models import Application

from django.db.models import Count
from django.http import JsonResponse

from django.core.mail import send_mail
from django.shortcuts import render, redirect
from users.models import User
from django.http import HttpResponse
from .models import Interview
import random
import string
from django.template.loader import render_to_string

from django.contrib.sites.shortcuts import get_current_site


# Configure logging
logger = logging.getLogger(__name__)


@login_required(login_url='login')
@company_belongs_to_user
def company_details(request, company_id):
    company = Company.objects.get(id=company_id)
    context = {
        "company": company,
    }
    return render(request, 'company/companyInfo.html', context)
#create company
@login_required(login_url='login')
def create_company(request):
    print("entered create company")
    try:
        company = request.user.company
        messages.warning(request, 'Permission Denied! You have already created a company.')
        return redirect('switch_account')
    except Company.DoesNotExist:
        if request.method == 'POST':
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
                messages.success(request, 'Company created successfully.')
                # Redirect to company_details with the newly created company's ID
                return redirect('update_company', company_id=company.id)  
            else:
                print(form.errors)  # This will print out form errors to the console
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
        else:
            form = CreateCompanyForm()

        context = {'form': form}
        return render(request, 'company/create_company.html', context)



@login_required(login_url='login')
@company_belongs_to_user
def update_company(request, company_id):
    company = get_object_or_404(Company, id=company_id, user=request.user)
    logger.debug(f"User {request.user} is updating company {company.name}")

    # Check if the logged-in user is a recruiter
    if request.user.is_recruiter:
        if request.method == 'POST':
            # Handle file uploads with request.FILES
            form = UpdateCompanyForm(request.POST, request.FILES, instance=company)
            logger.debug("Form data received: %s", request.POST)
            form.instance.user = request.user

            if form.is_valid():
                form.save()
                # Update user's has_company status after form submission
                request.user.has_company = True
                request.user.save()
                logger.debug("Company information updated successfully for company: %s", company.name)

                # Display a success message and redirect to 'view_my_jobs'
                messages.success(request, 'Your company information has been updated successfully.')
                return redirect('company_dashboard',company.id)
            else:
                # Log form errors
                logger.warning("Form errors: %s", form.errors)
                # Display a warning if form submission fails
                messages.warning(request, 'There was an issue with the form. Please correct the errors and try again.')
        else:
            # If not a POST request, render the form with the existing company instance
            form = UpdateCompanyForm(instance=company)
            logger.debug("Rendering form with existing company instance: %s", company.name)

        # Pass the form and company to the context
        context = {'form': form, 'company': company}
        return render(request, 'company/update_company.html', context)

    # Deny permission if the user is not a recruiter
    else:
        logger.warning("Permission Denied: User %s tried to access update_company", request.user)
        messages.warning(request, "Permission Denied. You don't have access to update company information.")
        return redirect('user_dashboard')


@login_required(login_url='login')
@company_belongs_to_user
def company_dashboard(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    
    jobs = Job.objects.filter(company=company).order_by('-created_at')  # Assuming `created_at` is your timestamp field
    
    # Add the number of applications to each job
    for job in jobs:
        job.application_count = Application.objects.filter(job=job).count()
    
    context = {
        'company': company,
        'jobs': jobs,  # Pass the jobs to the template
    }

    return render(request, 'company/dashboard.html', context)


@login_required(login_url='login')
@company_belongs_to_user
def view_my_jobs(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    jobs = Job.objects.filter(company=company).order_by('-created_at')
    
    for job in jobs:
        job.application_count = Application.objects.filter(job=job).count()
    
    context = {
        'company': company,
        'jobs': jobs,
    }
    return render(request, 'company/myJobs.html', context)

@login_required(login_url='login')
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
            resume = Resume.objects.filter(user=user).first()  # Use filter() to avoid DoesNotExist error

            if resume:  # Check if the user has a resume
                applicant_skills = set(resume.skills.all())
                job_skills = set(job.requirements.all())
                match_percentage, missing_skills = calculate_skill_match(applicant_skills, job_skills)
                application.matching_percentage = match_percentage

                # Calculate the quiz score (assumed to be stored in application.quiz_score)
                quiz_score = application.quiz_score

                # Calculate the overall score using match percentage and quiz score
                overall_score = match_percentage * 0.7 + (quiz_score / 10) * 0.3
                # Optionally, you can load user qualifications and skills for rendering in template
                application.user.skills_list = list(resume.skills.all())  # Create a separate attribute
                application.user.resume = resume
            else:
                # Handle cases where no resume exists (optional: set default values)
                application.matching_percentage = 0
                application.overall_score = application.quiz_score / 10 * 0.3  # Only quiz score
                application.user.skills_list = []
        job_applications[job] = applications

    context = {
        'company': company,
        'job_applications': job_applications,
        'applications': applications,
    }
    return render(request, 'company/candidates.html', context)




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

    print(f"Debug: Resume: {resume}, Resume Doc: {resume_doc}, Contact Info: {contact_info}, Profile: {profile}")  # Debugging output

    # Get work experiences related to the user
    work_experiences = WorkExperience.objects.filter(user=user).values('company_name', 'role', 'start_date', 'end_date')

    print(f"Debug: Work Experiences: {list(work_experiences)}")  # Debugging output

    # Get languages associated with the user's profile
    languages = UserLanguage.objects.filter(user_profile=profile).values('language__name')

    print(f"Debug: Languages: {list(languages)}")  # Debugging output

    data = {
        'first_name': resume.first_name if resume else user.first_name,
        'surname': resume.surname if resume else user.last_name,
        'state': resume.state if resume else None,
        'country': resume.country if resume else (profile.country if profile else None),
        'job_title': resume.job_title if resume else "No job title found",
        'date_of_birth': resume.date_of_birth if resume else "Date of birth not provided",
        'phone': resume.phone if resume else (contact_info.phone if contact_info else "Phone not provided"),
        'description': resume.description if resume else "No description available",
        'profile_image': resume.profile_image.url if resume and resume.profile_image else "No image available",
        'cv': resume.cv.url if resume and resume.cv else "No CV uploaded",
        'skills': list(resume.skills.values_list('name', flat=True)) if resume else [],
        'email': contact_info.email if contact_info else user.email,
        'resume_pdf': resume_doc.file.url if resume_doc and resume_doc.file else "No resume PDF available",
        'work_experiences': list(work_experiences),  # Include work experiences
        'languages': list(languages),  # Include languages
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
            application.user.skills_list = list(resume.skills.all())  # Add skills to user for rendering
            application.user.resume = resume
        else:
            # Handle cases where no resume exists
            application.matching_percentage = 0
            application.overall_score = application.quiz_score / 10 * 0.3  # Only quiz score
            application.user.skills_list = []

    # Sort applications based on quiz score, matching percentage, and randomly if there's a tie
    applications = sorted(applications, key=lambda x: (x.quiz_score, x.matching_percentage, random.random()), reverse=True)

    # Select top 5 applications and the next 5 for the waiting list
    top_5_applications = applications[:5]
    waiting_list_applications = applications[5:10]

    context = {
        'company': company,
        'job': job,
        'top_5_applications': top_5_applications,
        'waiting_list_applications': waiting_list_applications,
    }
    return render(request, 'company/job_applications.html', context)


@login_required(login_url='login')
@company_belongs_to_user
def view_application_details(request, application_id,company_id):
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
        'application': application,
        'company': company,

    }
    return render(request, 'company/application_details.html', context)
@login_required(login_url='login')
@company_belongs_to_user
def company_analytics(request, company_id):
    company = Company.objects.get(id=company_id)
    current_user = request.user
    if company.user != current_user:
        return HttpResponse("You are not authorized to view this page.")

    return render(request, 'company/analytics.html')


    
def company_inbox(request,company_id):
    company = Company.objects.get(id=company_id)
    current_user = request.user
    if company.user != current_user:
        return HttpResponse("You are not authorized to view this page.")

    return render(request, 'company/inbox.html',{'company':company})

def company_notifications(request,company_id):
    company = Company.objects.get(id=company_id)
    current_user = request.user
    if company.user != current_user:
        return HttpResponse("You are not authorized to view this page.")

    return render(request, 'company/notifications.html',{'company':company})

def company_detail_view(request, pk):
    company = get_object_or_404(Company, pk=pk)
    jobs = Job.objects.filter(company=company)
    is_owner = request.user == company.user
    applied_job_ids = []

    # Check if the user is authenticated before querying applications
    if request.user.is_authenticated:
        applied_job_ids = Application.objects.filter(user=request.user).values_list('job_id', flat=True)
    return render(request, 'company/company_detail.html', {'company': company, 'jobs': jobs,'applied_job_ids':applied_job_ids,'is_owner':is_owner})

def company_jobs_list_view(request, company_id):
    company = get_object_or_404(Company, id=company_id)
    jobs = Job.objects.filter(company=company)

    return render(request, 'company/company_jobs_list.html', {'company': company, 'jobs': jobs})



def company_list_view(request):
    companies = Company.objects.annotate(available_jobs=Count('job'))
    return render(request, 'company/company_list.html', {'companies': companies})



def generate_meeting_link():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))




def create_interview(request):
    if request.method == 'POST':
        candidate_id = request.POST.get('candidate_id')
        job_title = request.POST.get('job_title')
        date = request.POST.get('date')
        time = request.POST.get('time')
        timezone = request.POST.get('timezone')
        note = request.POST.get('note')
        
        candidate = User.objects.get(id=candidate_id)
        recruiter = request.user

        # Assuming job_title is unique and can be used to retrieve the job instance
        job = Job.objects.get(title=job_title)
        company_name = job.company.name  # Assuming the Company model has a 'name' field

        # Create the interview instance to get the room_id
        interview = Interview.objects.create(
            candidate=candidate,
            date=date,
            time=time,
            timezone=timezone,
            note=note
        )

        # Generate the meeting link using the room_id
        current_site = get_current_site(request)
        base_url = f"http://{current_site.domain}"
        meeting_link = f"{base_url}/chat/"
        room_id = interview.room_id
        interview.meeting_link = meeting_link
        interview.save()

        # Render email templates
        candidate_email_content = render_to_string('emails/candidate_interview_email.html', {
            'candidate': candidate,
            'job_title': job_title,
            'date': date,
            'time': time,
            'timezone': timezone,
            'meeting_link': meeting_link,
            'room_id': room_id,
            'note': note,
            'company_name': company_name
        })

        recruiter_email_content = render_to_string('emails/recruiter_interview_email.html', {
            'recruiter': recruiter,
            'candidate': candidate,
            'job_title': job_title,
            'date': date,
            'time': time,
            'timezone': timezone,
            'meeting_link': meeting_link,
            'room_id': room_id,
            'note': note,
            'company_name': company_name
        })

        # Send email to candidate
        send_mail(
            'Interview Scheduled',
            candidate_email_content,
            'from@example.com',
            [candidate.email],
            fail_silently=False,
            html_message=candidate_email_content
        )

        # Send email to recruiter
        send_mail(
            'Interview Scheduled',
            recruiter_email_content,
            'from@example.com',
            [recruiter.email],
            fail_silently=False,
            html_message=recruiter_email_content
        )

        return JsonResponse({'message': 'Interview created successfully.'})

    return JsonResponse({'error': 'Invalid request method.'}, status=400)