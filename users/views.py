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
from django.db.models import Q

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def handling_404(request, exception):
    return render(request, '404.html', status=404)
def index(request):
    return render(request, 'website/index.html')

from django.db.models import Avg
def home(request):
    jobs_list = Job.objects.all().order_by('-created_at')
    matching_jobs = Job.objects.annotate(max_matching_percentage=Avg('application__overall_match_percentage')).filter(max_matching_percentage__gte=10.0)
   
    # Get filter parameters from request
    salary_range = request.GET.get('salary_range')
    job_type = request.GET.getlist('job_type')
    experience_levels = request.GET.getlist('experience_levels')
    job_location = request.GET.get('job_location')
    search_query = request.GET.get('search_query')

    # Apply filters
    if salary_range:
        jobs_list = jobs_list.filter(salary__lte=salary_range)

    if job_type:
        jobs_list = jobs_list.filter(job_type__in=job_type)

    if experience_levels:
        jobs_list = jobs_list.filter(experience_levels__in=experience_levels)

    if job_location:
        if job_location == "onsite":
            jobs_list = jobs_list.filter(job_location_type="Onsite")
        elif job_location == "remote":
            jobs_list = jobs_list.filter(job_location_type="Remote")

    if search_query:
        jobs_list = jobs_list.filter(
            Q(title__icontains=search_query) |
            Q(company__name__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(job_type__icontains=search_query) |
            Q(experience_levels__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(jobs_list, 7)  # Show 10 jobs per page
    page = request.GET.get('page')

    try:
        jobs = paginator.page(page)
    except PageNotAnInteger:
        jobs = paginator.page(1)
    except EmptyPage:
        jobs = paginator.page(paginator.num_pages)

    context = {
        'jobs': jobs,
        'matching_jobs':matching_jobs,
    }
    return render(request, 'website/home.html', context)



# login a user
def login_user(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return redirect('/')  # Update this to the appropriate URL
        else:
            messages.warning(request, 'Email or password incorrect')
            return render(request, 'users/login.html')
    else:
        return render(request, 'users/login.html')

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
            
            # Log the user in with the specified backend
            backends = get_backends()
            for backend in backends:
                if hasattr(backend, 'get_user'):
                    backend_name = f'{backend.__module__}.{backend.__class__.__name__}'
                    break
            login(request, user, backend=backend_name)
            
            messages.success(request, 'Your account has been created successfully and you are now logged in.')
            
            # Redirect to switch account
            return redirect('switch_account')
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
    print("entered recreuuu")
    if request.method == 'POST':
        print("posteeeeeeeeeeeeeeeeeeeeeed")
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
    messages.info(request, 'Your session has ended')
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
    user = request.user

    # Handle case where user may not have a company
    company = Company.objects.filter(user=user).first()

    print(f"Initial: is_applicant={user.is_applicant}, is_recruiter={user.is_recruiter}")

    if user.is_applicant:
        if not user.has_company:
            user.is_recruiter = True
            user.is_applicant = False
            user.save()
            print(f"Switched to recruiter: is_applicant={user.is_applicant}, is_recruiter={user.is_recruiter}")
            messages.success(request, 'You have switched to a recruiter account.')
            return redirect(reverse('create_company'))
        else:
            messages.info(request, 'You already have a company associated with your account.')
            if company:
                user.is_recruiter = True
                user.is_applicant = False
                user.save()
                print(f"Switched to recruiter with company: is_applicant={user.is_applicant}, is_recruiter={user.is_recruiter}")
                return redirect(reverse('view_applications', args=[company.id]))
            else:
                messages.error(request, 'An error occurred: No company found.')
                return redirect(reverse('home'))
    elif user.is_recruiter:
        user.is_applicant = True
        user.is_recruiter = False
        user.save()
        print(f"Switched to applicant: is_applicant={user.is_applicant}, is_recruiter={user.is_recruiter}")
        if not ResumeDoc.objects.filter(user=user).exists():
            messages.success(request, 'You have switched to an applicant account. Please complete your resume.')
            return redirect('switch_account')
        else:
            messages.success(request, 'You have switched to an applicant account.')
            return redirect('dashboard')
    else:
        messages.error(request, 'An error occurred while switching account types.')

    return redirect(reverse('home'))