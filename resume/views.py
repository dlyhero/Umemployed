from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Resume, SkillCategory, Skill
from .forms import UpdateResumeForm, UpdateResumeForm2, UpdateResumeForm3,CategoryForm,SkillForm
from users.models import User
from job.models import Job
from onboarding.views import general_knowledge_quiz
from django.contrib.auth.decorators import login_required
from geopy.distance import geodesic
from geopy.geocoders import OpenCage
geocoder = OpenCage('70d694d4b6824310a0a7e3a4f5041ce3')  # Replace 'YOUR_API_KEY' with your actual OpenCage API key


@login_required(login_url='login')
def update_resume(request):
    if request.user.is_applicant:
        try:
            resume = Resume.objects.get(user=request.user)
        except Resume.DoesNotExist:
            resume = None

        if request.method == 'POST':
            form = UpdateResumeForm(request.POST, request.FILES, instance=resume)
            if form.is_valid():
                var = form.save(commit=False)
                var.user = request.user
                var.save()

                # Update user.has_resume field
                user = request.user
                user.has_resume = True
                user.save()

                messages.info(request, 'Your resume info has been updated.')
                return redirect('select_category')
            else:
                messages.warning(request, 'Something went wrong')
        else:
            form = UpdateResumeForm(instance=resume)

        context = {'form': form}
        return render(request, 'resume/update_resume.html', context)
    else:
        messages.warning(request, "Permission Denied")
        return redirect('dashboard')


from django.shortcuts import render, redirect
from .forms import CategoryForm, SkillForm

def select_category(request):
    if request.user.is_applicant:
        if request.method == 'POST':
            form = CategoryForm(request.POST)
            if form.is_valid():
                request.session['selected_category'] = form.cleaned_data['category'].id
                return redirect('select_skills')
        else:
            form = CategoryForm()
        
        return render(request, 'resume/select_category.html', {'form': form})
    else:
        messages.warning(request, "Permission Denied")
        return redirect('dashboard')

def select_skills(request):
    if request.user.is_applicant:
        selected_category_id = request.session.get('selected_category')
        if selected_category_id:
            selected_category = SkillCategory.objects.get(id=selected_category_id)
            if request.method == 'POST':
                form = SkillForm(request.POST, category=selected_category)
                if form.is_valid():
                    resume = Resume.objects.get(user=request.user)
                    resume.category = selected_category
                    resume.skills.set(form.cleaned_data['skills'])
                    resume.save()
                    return redirect('onboarding-3')
            else:
                form = SkillForm(category=selected_category)
            
            return render(request, 'resume/select_skills.html', {'form': form})
        else:
            # Handle the case where a category is not selected
            return redirect('select_category')
    else:
        messages.warning(request, "Permission Denied")
        return redirect('dashboard')




@login_required(login_url='login')
def applicant_onboarding_part3(request):
    if request.user.is_applicant:
        resume = get_object_or_404(Resume, user=request.user)

        if request.method == 'POST':
            form = UpdateResumeForm3(request.POST, request.FILES, instance=resume)
            if form.is_valid():
                var = form.save(commit=False)
                var.save()

                messages.info(request, 'Your resume information has been updated.')
                return redirect('matching_jobs')
            else:
                messages.warning(request, 'Something went wrong')
        else:
            form = UpdateResumeForm3(instance=resume)

        context = {
            'form': form
        }
        return render(request, 'resume/applicant_onboarding_part3.html', context)
    else:
        messages.warning(request, "Permission Denied")
        return redirect('dashboard')



def calculate_skill_match(applicant_skills, job_skills):
    common_skills = applicant_skills.intersection(job_skills)
    match_percentage = (len(common_skills) / len(job_skills)) * 100
    return match_percentage, job_skills - common_skills  # Missing skills

def calculate_proximity_percentage(user_location, job_location):
    user_coordinates = get_coordinates(user_location)
    job_coordinates = get_coordinates(job_location)
    if user_coordinates and job_coordinates:
        distance_km = geodesic(user_coordinates, job_coordinates).km
        if distance_km <= 50:  # Adjust the proximity threshold as needed
            return 10  # Assign an additional 10% match for jobs within 50 km
    return 0

def get_coordinates(location):
    try:
        result = geocoder.geocode(location)
        if result:
            latitude = result[0]['geometry']['lat']
            longitude = result[0]['geometry']['lng']
            return latitude, longitude
    except Exception as e:
        print(f"Error retrieving coordinates for {location}: {e}")
    
    return None

# @login_required(login_url='login')
def get_matching_jobs(user_job_title, user_skills):
    all_jobs = Job.objects.all()
    matching_jobs = []

    for job in all_jobs:
        job_skills = set(job.requirements.all())
        if job_skills.intersection(user_skills):
            match_percentage, missing_skills = calculate_skill_match(user_skills, job_skills)
            proximity_percentage = calculate_proximity_percentage(user_job_title, job.location)  # Fix the parameter to user_job_title
            total_match_percentage = match_percentage + proximity_percentage
            matching_jobs.append({'job': job, 'match_percentage': total_match_percentage, 'missing_skills': missing_skills})
    
    return matching_jobs

@login_required(login_url='login')
def display_matching_jobs(request):
    user_resume = Resume.objects.get(user=request.user)
    user_job_title = user_resume.job_title
    user_skills = set(user_resume.skills.all())  # Assuming skills are stored in a ManyToManyField

    matching_jobs_data = get_matching_jobs(user_job_title, user_skills)

    matching_jobs = []
    for job_data in matching_jobs_data:
        job = job_data['job']
        job_skills = set(job.requirements.all())
        match_percentage, missing_skills = calculate_skill_match(user_skills, job_skills)
        job_dict = {
            'company': {
                'logo': {'url': job.company.logo.url},
                'name': job.company.name
            },
            'id':job.id,
            'title': job.title,
            'location': job.location,
            'is_available': job.is_available,
            'salary': job.salary,
            'description': job.description,
            'match_percentage': match_percentage,
            'missing_skills': list(missing_skills)  # Convert set to list for iteration in HTML
        }
        matching_jobs.append(job_dict)
    for job in matching_jobs:
        print(job)

    context = {'matching_jobs': matching_jobs}
    return render(request, 'job/matching_jobs.html', context)















def resume_details(request, pk):
    resume = get_object_or_404(Resume, pk=pk)
    context = {'resume': resume}
    return render(request, 'resume/resume_details.html', context)