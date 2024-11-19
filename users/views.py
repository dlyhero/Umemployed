from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import User
from .forms import RegisterUserForm
from resume.models import Resume
from company.models import Company
from company.views import create_company
from django.contrib.auth.decorators import login_required
from job.models import Job,Application
from .filters import OrderFilter
from django.db.models import Q,Count
from job.models import calculate_skill_match 
from allauth.account.utils import send_email_confirmation

from allauth.account.views import ConfirmEmailView
from allauth.account.models import EmailConfirmationHMAC
from django.contrib.auth import login
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from job.models import SavedJob
from urllib.parse import urlencode
from .forms import CustomSetPasswordForm
from django.contrib.auth import update_session_auth_hash

from django.http import HttpResponseRedirect
from django.core.mail import send_mail
from django.conf import settings

from allauth.account.models import EmailAddress
import logging
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.urls import reverse  # Import reverse
from resume.models import ResumeDoc
from django.contrib.auth import get_backends


def handling_404(request, exception):
    return render(request, '404.html', status=404)

def index(request):
    user = request.user
    if request.user.is_authenticated and not request.user.has_usable_password():
        messages.warning(request, 'Please set a password to secure your account.')
        return redirect('set_password')
    
    recent_jobs = Job.objects.filter(job_creation_is_complete=True).order_by('-created_at')[:10]
    job_count = Job.objects.filter(job_creation_is_complete=True).count()

    # Get the IDs of jobs the user has applied for
    applied_job_ids = []
    if request.user.is_authenticated:
        applied_job_ids = Application.objects.filter(user=request.user).values_list('job_id', flat=True)
        saved_job_ids = SavedJob.objects.filter(user=request.user).values_list('job_id', flat=True)
    else:
        saved_job_ids = []

    featured_companies = Company.objects.all()[:4]

    context = {
        'job_count': job_count,
        'recent_jobs': recent_jobs,
        'featured_companies': featured_companies,
        'applied_job_ids': applied_job_ids,
        'saved_jobs': saved_job_ids
    }

    return render(request, 'website/index.html', context)

@login_required
def set_password(request):
    if request.method == 'POST':
        form = CustomSetPasswordForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important, to update the session with the new password
            messages.success(request, 'Your password has been set successfully!')
            return redirect('switch_account')  # Redirect to the index page or any other page
    else:
        form = CustomSetPasswordForm(user=request.user)
    return render(request, 'users/set_password.html', {'form': form})


def home(request):
    user = request.user
    matching_jobs = []
    non_matching_jobs = []

    # Step 1: Retrieve all complete jobs
    all_jobs = Job.objects.filter(job_creation_is_complete=True)

    # If the user is authenticated, retrieve applied job IDs
    if user.is_authenticated:
        applied_job_ids = Application.objects.filter(user=user).values_list('job_id', flat=True)
        saved_job_ids = SavedJob.objects.filter(user=request.user).values_list('job_id', flat=True)
    else:
        applied_job_ids = []
        saved_job_ids = []

    # Get filtering parameters from the GET request
    salary_range = request.GET.get('salary_range')
    job_type = request.GET.getlist('job_type')
    experience_levels = request.GET.getlist('experience_levels')
    location_query = request.GET.get('location_query')
    search_query = request.GET.get('search_query')
    remote = request.GET.get('remote')
    applicants = request.GET.get('applicants')

    # Initialize an empty Q object for OR conditions
    query = Q()

    # Apply OR filters based on user input
    if salary_range:
        try:
            min_salary, max_salary = map(int, salary_range.split('-'))
            query |= Q(salary__gte=min_salary) & Q(salary__lte=max_salary)
        except ValueError:
            pass  # Invalid salary range provided, skip this filter

    if job_type:
        query |= Q(job_type__in=job_type)

    if experience_levels:
        query |= Q(experience_levels__in=experience_levels)

    if search_query:
        query |= Q(
            Q(title__icontains=search_query) |
            Q(company__name__icontains=search_query) |
            Q(location__icontains=search_query)
        )

    if location_query:
        query |= Q(location__icontains=location_query)

    if remote == 'on':
        query |= Q(job_location_type__icontains='remote')

    if applicants:
        all_jobs = all_jobs.annotate(applicant_count=Count('application'))
        if applicants == 'Less than 10':
            query |= Q(applicant_count__lt=10)
        elif applicants == '10 to 50':
            query |= Q(applicant_count__gte=10, applicant_count__lte=50)
        elif applicants == '50 to 100':
            query |= Q(applicant_count__gte=50, applicant_count__lte=100)
        elif applicants == 'More than 100':
            query |= Q(applicant_count__gt=100)

    # Apply the ORed query to filter jobs
    filtered_jobs = all_jobs.filter(query).distinct()

    # Debugging output
    print("Query:", query)
    print("Filtered jobs count:", filtered_jobs.count())

    # If the user is authenticated, match jobs by skills
    if user.is_authenticated:
        try:
            applicant_resume = Resume.objects.get(user=user)
            applicant_skills = set(applicant_resume.skills.all())
        except Resume.DoesNotExist:
            applicant_skills = set()

        for job in filtered_jobs:
            job_skills = set(job.requirements.all())
            match_percentage, _ = calculate_skill_match(applicant_skills, job_skills)

            if match_percentage >= 10.0:
                matching_jobs.append((job, match_percentage))
            else:
                non_matching_jobs.append(job)
    else:
        non_matching_jobs = list(filtered_jobs)

    matching_jobs = sorted(matching_jobs, key=lambda x: x[1], reverse=True)

    paginator = Paginator(non_matching_jobs, 6)
    page = request.GET.get('page')

    try:
        jobs = paginator.page(page)
    except PageNotAnInteger:
        jobs = paginator.page(1)
    except EmptyPage:
        jobs = paginator.page(paginator.num_pages)

    # Create a dictionary for the URL parameters
    params = {
        'search_query': search_query,
        'location_query': location_query,
        'job_type': job_type if job_type else None,
        'salary_range': salary_range,
        'experience_levels': experience_levels if experience_levels else None,
        'remote': remote,
        'applicants': applicants,
    }

    # Filter out None values to avoid passing empty parameters
    filtered_params = {k: v for k, v in params.items() if v}

    # Create the URL-encoded query string
    query_string = urlencode(filtered_params)

    context = {
        'jobs': jobs,
        'matching_jobs': matching_jobs,
        'applied_job_ids': applied_job_ids,
        'query_string': query_string,
        'saved_jobs': saved_job_ids,
    }
    return render(request, 'website/home.html', context)



def login_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        if user is not None and user.is_active:
            login(request, user)
            # Redirect to the 'next' URL if provided, otherwise to the home page
            next_url = request.POST.get('next') or request.GET.get('next') or '/'
            return HttpResponseRedirect(next_url)
        else:
            messages.warning(request, 'Email or password incorrect')
            return render(request, 'users/login.html', {'next': request.POST.get('next') or request.GET.get('next')})
    else:
        # Pass 'next' parameter to the login template for use in the form
        next_url = request.GET.get('next', '/')
        return render(request, 'users/login.html', {'next': next_url})


def register_applicant(request):
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            # Save the user
            user = form.save(commit=False)
            user.is_applicant = True
            user.username = user.email
            user.save()
            
            # Create Resume instance
            Resume.objects.create(user=user)
            
            # Send email confirmation
            send_email_confirmation(request, user)
            
            # Log the user in with the specified backend
            backends = get_backends()
            for backend in backends:
                if hasattr(backend, 'get_user'):
                    backend_name = f'{backend.__module__}.{backend.__class__.__name__}'
                    break
            login(request, user, backend=backend_name)
            
            
            # Redirect to switch account or any other desired page
            return redirect('account_email_verification_sent')
        else:
            # Display form errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = RegisterUserForm()
    
    return render(request, 'users/register_applicant.html', {'form': form})

# register recruiter only
def register_recruiter(request):
    if request.method == 'POST':
        is_recruiter = request.POST.get('is_recruiter')  # Get the value of the checkbox
        if is_recruiter:
            request.user.is_recruiter = True
            request.user.save()
            messages.info(request, 'Your account has been updated successfully')
            return redirect("create_company")
        else:
            messages.info(request, 'Your account has been updated successfully')
            return redirect("login")
    else:
        form = RegisterUserForm()
    return render(request, 'users/register_recruiter.html', {'form': form})
    
# logout a user
@login_required(login_url='/')
def logout_user(request):
    logout(request)
    return redirect('index')  # Update the target name to match the appropriate URL name

@login_required(login_url='/')
def switch_account(request):
    if request.user.is_authenticated and not request.user.has_usable_password():
        messages.warning(request, 'Please set a password to secure your account.')
        return redirect('set_password')
    
    return render(request,'users/accountType.html')


@login_required
def change_account_type(request):
    user=request.user
    print(f"Ussser is_applicant: {user.is_applicant}, is_recruiter: {user.is_recruiter}")

    return render(request, 'users/changeAccountType.html')



@login_required
def switch_account_type(request):
    new_role = request.GET.get('new_role', None)
    user = request.user

    print(f"Before switch: is_applicant={user.is_applicant}, is_recruiter={user.is_recruiter}")

    if new_role == 'Job Seeker':
        if not ResumeDoc.objects.filter(user=user).exists():
            messages.success(request, 'You need to complete your resume before switching to an applicant account.')
            return redirect('switch_account')
        else:
            user.is_applicant = True
            user.is_recruiter = False
            user.save()
            print(f"Switched to Job Seeker: is_applicant={user.is_applicant}, is_recruiter={user.is_recruiter}")
            messages.success(request, 'You have switched to a Job Seeker account.')
            return redirect('dashboard')
    elif new_role == 'Employer':
        if not user.has_company:
            user.is_recruiter = True
            user.is_applicant = False
            user.save()
            print(f"Switched to Employer without company: is_applicant={user.is_applicant}, is_recruiter={user.is_recruiter}")
            messages.success(request, 'You have switched to a recruiter account.')
            return redirect(reverse('create_company'))
        else:
            user.is_recruiter = True
            user.is_applicant = False
            user.save()
            print(f"Switched to Employer with company: is_applicant={user.is_applicant}, is_recruiter={user.is_recruiter}")
            messages.success(request, 'You have switched to a recruiter account.')
            return redirect(reverse('company_dashboard', args=[user.company.id]))
    else:
        messages.error(request, 'Invalid role switch request.')
        return redirect('home')
    
from notifications.utils import notify_user
@login_required
def user_dashboard(request):
    user = request.user
    recommended_jobs = Job.objects.all()[:5]
    applied_job_ids = Application.objects.filter(user=user).values_list('job_id', flat=True)
    
    # Calculate profile completion percentage
    resume = Resume.objects.filter(user=user).first()
    if resume:
        completion_percentage = resume.calculate_completion_percentage()
    else:
        completion_percentage = 0

    context = {
        'recommended_jobs': recommended_jobs,
        'applied_job_ids': applied_job_ids,
        'completion_percentage': completion_percentage,
    }
    return render(request, 'website/user_dashboard.html', context)


# view to request unverified users to verify emails

def send_verification_to_unverified_users(request):
    User = get_user_model()
    
    for user in User.objects.filter(is_active=True):
        email_address, created = EmailAddress.objects.get_or_create(user=user, email=user.email)
        if not email_address.verified:
            email_address.send_confirmation()
            print(f"Email confirmation sent to {user.email}")
    
    return HttpResponse("Verification emails sent to unverified users.")


class CustomConfirmEmailView(ConfirmEmailView):

    def get(self, request, *args, **kwargs):
        # Confirm the email
        self.object = confirmation = self.get_object()

        confirmation.confirm(request)

        # Automatically log the user in
        user = confirmation.email_address.user
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        # Redirect to your desired page after login
        return redirect('switch_account')  # Change to your desired URL name or path




logger = logging.getLogger(__name__)

@login_required
def resend_verification_email(request):
    logger.info("Resending verification email for user: %s", request.user.email)
    send_email_confirmation(request, request.user)
    print("Email confirmation sent successfully:", request.user.email)
    return redirect('account_email_verification_sent')


def resend_confirmation_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            send_confirmation_email(user)
            messages.success(request, 'Confirmation email sent successfully.')
        except User.DoesNotExist:
            messages.error(request, 'User with that email does not exist.')
        return redirect('login')  # Replace 'your_login_url' with the actual URL of your login page

    return render(request, 'resend_confirmation_email.html')  # Replace 'resend_confirmation_email.html' with the actual template name
def send_confirmation_email(user):
    subject = 'Confirm Your Email'
    message = f'Please click the following link to confirm your email: {user.get_confirmation_link()}'
    from_email = 'brandipearl123@gmail.com'  # Replace with your email address
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list)
    
# Custom 404 error page
def custom_404_view(request, exception):
    return render(request, '404.html', status=404)

# Custom 500 error page
def custom_500_view(request):
    return render(request, '500.html', status=500)

def career_resources(request):
    return render(request, 'website/carreer_resources.html')

def feature_not_implemented(request):
    return render(request, 'modal.html') 

#user umemployed resume
from resume.models import  Resume, Education, WorkExperience, UserLanguage, ContactInfo

def user_resume(request, user_id):
    user = get_object_or_404(User, id=user_id)
    resume = get_object_or_404(Resume, user=user)
    education_list = Education.objects.filter(user=user)
    work_experiences = WorkExperience.objects.filter(user=user)
    languages = UserLanguage.objects.filter(user_profile__user=user)
    contact_info = get_object_or_404(ContactInfo, user=user)

    context = {
        'user': user,
        'resume': resume,
        'education_list': education_list,
        'work_experiences': work_experiences,
        'languages': languages,
        'contact_info': contact_info,
    }
    return render(request, 'users/resume_template.html', context)