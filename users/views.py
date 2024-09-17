from django.shortcuts import render, redirect
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

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def handling_404(request, exception):
    return render(request, '404.html', status=404)
def index(request):
    
    recent_jobs = Job.objects.order_by('-created_at')[:10]
    job_count = Job.objects.count()
    
    featured_companies = Company.objects.all()
    context={
        'job_count':job_count,
        'recent_jobs':recent_jobs,
        'featured_companies':featured_companies
    }
    return render(request, 'website/index.html',context)

from django.db.models import Q, Count

def home(request):
    user = request.user
    matching_jobs = []
    non_matching_jobs = []

    # Step 1: Retrieve all jobs
    all_jobs = Job.objects.all()
    print(f"DEBUG: All Jobs in System (Count: {all_jobs.count()}): {list(all_jobs)}")

    # Apply filters to all jobs before splitting them into matching/non-matching
    salary_range = request.GET.get('salary_range')
    job_type = request.GET.getlist('job_type')
    experience_levels = request.GET.getlist('experience_levels')
    job_location = request.GET.get('job_location')
    search_query = request.GET.get('search_query')
    location_query = request.GET.get('location_query')
    applicants = request.GET.get('applicants')  # Get applicants filter value

    if salary_range:
        all_jobs = all_jobs.filter(salary__lte=salary_range)

    if job_type:
        all_jobs = all_jobs.filter(job_type__in=job_type)

    if experience_levels:
        all_jobs = all_jobs.filter(experience_levels__in=experience_levels)

    if job_location:
        all_jobs = all_jobs.filter(job_location_type__in=job_location)

    if location_query:
        all_jobs = all_jobs.filter(location__icontains=location_query)

    if search_query:
        all_jobs = all_jobs.filter(
            Q(title__icontains=search_query) |
            Q(company__name__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(job_type__icontains=search_query) |
            Q(experience_levels__icontains=search_query)
        )

    if applicants:
        all_jobs = all_jobs.annotate(applicant_count=Count('application'))
        if applicants == 'Less than 10':
            all_jobs = all_jobs.filter(applicant_count__lt=10)
        elif applicants == '10 to 50':
            all_jobs = all_jobs.filter(applicant_count__gte=10, applicant_count__lte=50)
        elif applicants == '50 to 100':
            all_jobs = all_jobs.filter(applicant_count__gte=50, applicant_count__lte=100)
        elif applicants == 'More than 100':
            all_jobs = all_jobs.filter(applicant_count__gt=100)

    print(f"DEBUG: Filtered Jobs (Count: {all_jobs.count()}): {list(all_jobs)}")

    if user.is_authenticated:
        try:
            applicant_resume = Resume.objects.get(user=user)
            applicant_skills = set(applicant_resume.skills.all())
            print(f"DEBUG: Applicant Skills: {list(applicant_skills)}")
        except Resume.DoesNotExist:
            applicant_skills = set()
            print("DEBUG: Applicant Resume does not exist. Applicant skills set to empty.")

        for job in all_jobs:
            job_skills = set(job.requirements.all())
            match_percentage, _ = calculate_skill_match(applicant_skills, job_skills)

            print(f"DEBUG: Job '{job.title}' (ID: {job.id}) - Match Percentage: {match_percentage}")

            if match_percentage >= 10.0:  # Threshold of 10%
                matching_jobs.append((job, match_percentage))
            else:
                non_matching_jobs.append(job)

        print(f"DEBUG: Matching Jobs (Count: {len(matching_jobs)}): {matching_jobs}")
        print(f"DEBUG: Non-Matching Jobs (Count: {len(non_matching_jobs)}): {non_matching_jobs}")

    else:
        # If user is not authenticated, all jobs are considered non-matching
        non_matching_jobs = list(all_jobs)

    # Pagination
    paginator = Paginator(non_matching_jobs, 6)  # Show 7 jobs per page
    page = request.GET.get('page')

    try:
        jobs = paginator.page(page)
    except PageNotAnInteger:
        jobs = paginator.page(1)
    except EmptyPage:
        jobs = paginator.page(paginator.num_pages)

    context = {
        'jobs': jobs,
        'matching_jobs': matching_jobs,  # Matching jobs section
        'non_matching_jobs': jobs,  # Non-matching jobs section
    }
    return render(request, 'website/home.html', context)


# login a user
from django.http import HttpResponseRedirect

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


# views.py
from django.contrib.auth import get_backends
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
            
            messages.success(request, 'Your account has been created successfully. Please check your email to confirm your account.')
            
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
    return redirect('home')  # Update the target name to match the appropriate URL name

def switch_account(request):
    return render(request,'users/accountType.html')


@login_required
def change_account_type(request):
    user=request.user
    print(f"Ussser is_applicant: {user.is_applicant}, is_recruiter: {user.is_recruiter}")

    return render(request, 'users/changeAccountType.html')

from django.urls import reverse  # Import reverse
from resume.models import ResumeDoc
@login_required
def switch_account_type(request):
    print("4$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
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
            return redirect(reverse('view_applications', args=[user.company.id]))
    else:
        messages.error(request, 'Invalid role switch request.')
        return redirect('home')
    
@login_required
def user_dashboard(request):
    # Fetch only the first 3 jobs
    recommended_jobs = Job.objects.all()[:5]
    context = {
        'recommended_jobs': recommended_jobs,
    }
    return render(request, 'website/user_dashboard.html', context)


# view to request unverified users to verify emails
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress
from django.http import HttpResponse


def send_verification_to_unverified_users(request):
    User = get_user_model()
    
    for user in User.objects.filter(is_active=True):
        email_address, created = EmailAddress.objects.get_or_create(user=user, email=user.email)
        if not email_address.verified:
            email_address.send_confirmation()
            print(f"Email confirmation sent to {user.email}")
    
    return HttpResponse("Verification emails sent to unverified users.")

from allauth.account.views import ConfirmEmailView
from allauth.account.models import EmailConfirmationHMAC
from django.shortcuts import redirect
from django.contrib.auth import login

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


from django.core.mail import send_mail
from django.conf import settings
    
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