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

def home(request):
    job_list = Job.objects.all()    
    jobs = Job.objects.all().first()
    job = Job.objects.first()
    applications = Application.objects.filter(job=job).count()
    job_filter = OrderFilter(request.GET, queryset=job_list)
    
    search_query = request.GET.get('search_query', '')
    if search_query:
        job_filter = job_filter.filter(
            Q(title__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    context = {'jobs':jobs, 
               'jobs': job_filter.qs, 
               'myFilter': job_filter,
                'applications':applications,}
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
from django.http import JsonResponse

from django.http import JsonResponse

@login_required
def change_account_type(request):

    return render(request, 'users/changeAccountType.html')

from django.urls import reverse  # Import reverse
from resume.models import ResumeDoc
@login_required
def switch_account_type(request):
    print("clicked")
    user = request.user

    if user.is_applicant:
        if not user.has_company:
            user.is_recruiter = True
            user.is_applicant = False
            user.save()
            messages.success(request, 'You have switched to a recruiter account.')
            return redirect(reverse('create_company'))
        else:
            messages.info(request, 'You already have a company associated with your account.')
    elif user.is_recruiter:
        user.is_applicant = True
        user.is_recruiter = False
        user.save()
        if not ResumeDoc.objects.filter(user=user).exists():
            messages.success(request, 'You have switched to an applicant account.')
            return redirect('dashboard')
        else:
            messages.success(request, 'You have switched to an applicant account.')
    else:
        messages.error(request, 'An error occurred while switching account types.')

    return redirect(reverse('home'))