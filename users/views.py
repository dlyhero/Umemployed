from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from .models import User
from .forms import RegisterUserForm
from resume.models import Resume
from company.models import Company
from company.views import create_company
from django.contrib.auth.decorators import login_required
from job.models import Job
from .filters import OrderFilter
from django.db.models import Q

def home(request):
    job_list = Job.objects.all()
    job_filter = OrderFilter(request.GET, queryset=job_list)
    
    search_query = request.GET.get('search_query', '')
    if search_query:
        job_filter = job_filter.filter(
            Q(title__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    context = {'jobs': job_filter.qs, 'myFilter': job_filter}
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

# register applicant
def register_applicant(request):
    if request.method == 'POST':
        form = RegisterUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_applicant = True
            user.username = user.email
            user.save()
            Resume.objects.create(user=user)
            messages.success(request, 'Your account has been created successfully')
            return redirect("login")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return render(request, 'users/register_applicant.html', {'form': form})
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
    messages.info(request, 'Your session has ended')
    return redirect('home')  # Update the target name to match the appropriate URL name
