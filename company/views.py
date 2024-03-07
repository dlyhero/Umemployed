from django.shortcuts import render,redirect

from django.contrib import messages
from .models import Company
from users.models import User
from .forms import UpdateCompanyForm, CreateCompanyForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from resume.views import calculate_skill_match




#create company
def create_company(request):
    try:
        company = request.user.company
        messages.warning(request, 'Permission Denied! You have already created a company.')
        return redirect('dashboard')
    except Company.DoesNotExist:
        if request.method == 'POST':
            form = CreateCompanyForm(request.POST)
            if form.is_valid():
                company = form.save(commit=False)
                company.user = request.user
                company.save()
                request.user.has_company = True
                request.user.save()
                messages.success(request, 'Company created successfully.')
                return redirect('dashboard')  # Redirect to the dashboard after successful company creation
            else:
                messages.error(request, 'Error creating company.')
        else:
            form = CreateCompanyForm()

        context = {'form': form}
        return render(request, 'company/create_company.html', context)


#update company
@login_required(login_url='login')
def update_company(request):
    if request.user.is_recruiter:
        company = get_object_or_404(Company, user=request.user)

        if request.method == 'POST':
            form = UpdateCompanyForm(request.POST, instance=company)
            if form.is_valid():
                var = form.save(commit=False)
                user = request.user
                user.has_company = True
                var.save()
                user.save()
                messages.info(request, 'Your company info has been Updated.')
                return redirect('dashboard')
            else:
                messages.warning(request, 'Something went wrong.')
        else:
            form = UpdateCompanyForm(instance=company)
        
        context = {'form': form}
        return render(request, 'company/update_company.html', context)
    else:
        messages.warning(request,"Permission Denied")

@login_required(login_url='login')
def company_details(request, pk):
    company = get_object_or_404(Company, pk=pk)
    context = {'company': company}
    return render(request, 'company/company_details.html', context)

from django.shortcuts import render
from django.http import HttpResponse
from job.models import Job, Application
from resume.models import Resume

@login_required(login_url='login')
def view_applications(request, company_id):
    # Check if the current user is the owner of the company
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
            resume = Resume.objects.get(user=user)
            applicant_skills = set(resume.skills.all())
            job_skills = set(job.requirements.all())
            match_percentage, missing_skills = calculate_skill_match(applicant_skills, job_skills)
            application.matching_percentage = match_percentage
            # Calculate the quiz score (assumed to be stored in application.quiz_score)
            quiz_score = application.quiz_score

            # Calculate the overall score using match percentage and quiz score
            overall_score = match_percentage * 0.7 + (quiz_score / 10) * 0.3
            application.overall_score = overall_score

    context = {
        'company': company,
        'job_applications': job_applications,
    }
    return render(request, 'company/view_applications.html', context)



@login_required(login_url='login')
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

def company_analytics(request, company_id):
    company = Company.objects.get(id=company_id)
    current_user = request.user
    if company.user != current_user:
        return HttpResponse("You are not authorized to view this page.")

    return render(request, 'company/analytics.html')