import requests
from geopy.distance import geodesic
from geopy.geocoders import OpenCage
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ContactInfoForm , CategoryForm, SkillForm, UpdateResumeForm, UpdateResumeForm2, UpdateResumeForm3
from .models import Resume, SkillCategory, Skill, ResumeDoc, ContactInfo
from users.models import User
from job.models import Job
from onboarding.views import general_knowledge_quiz
from .extract_pdf import upload_resume

geocoder = OpenCage('70d694d4b6824310a0a7e3a4f5041ce3')  # Replace 'YOUR_API_KEY' with your actual OpenCage API key


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ContactInfoForm
from .models import ContactInfo
from notifications.utils import notify_user

from django.contrib import messages

@login_required
def update_resume(request):
    try:
        contact_info = ContactInfo.objects.get(user=request.user)
    except ContactInfo.DoesNotExist:
        contact_info = None

    try:
        # Try to get the existing resume for the user
        resume = Resume.objects.get(user=request.user)
    except Resume.DoesNotExist:
        # Initialize the Resume object with default or placeholder values
        resume = Resume(user=request.user, job_title="Default Title")  # Use a default job title or other defaults
        resume.save()  # Save it with basic fields

    if request.method == "POST":
        form = ContactInfoForm(request.POST, request.FILES, instance=contact_info)
        
        if form.is_valid():
            # Save or update ContactInfo
            contact_info = form.save(commit=False)
            contact_info.user = request.user
            contact_info.save()

            # Update corresponding Resume fields from ContactInfo
            resume.first_name = contact_info.name.split()[0] if contact_info.name else resume.first_name  # Assuming first_name is the first part of the full name
            resume.surname = " ".join(contact_info.name.split()[1:]) if contact_info.name else resume.surname  # Assuming surname is the rest of the name
            resume.phone = contact_info.phone
            resume.country = contact_info.country.name if contact_info.country else resume.country  # CountryField is different from CharField, use .name for its value

            # Handle the job title update logic
            job_title_id = request.POST.get("job_title")
            other_job_title = request.POST.get("other_job_title")

            if job_title_id:
                try:
                    job_title = SkillCategory.objects.get(id=job_title_id).name
                    resume.job_title = job_title  # Update job title with selected option
                except SkillCategory.DoesNotExist:
                    messages.error(request, "Selected job title does not exist.")
            elif other_job_title:
                resume.job_title = other_job_title  # Set the job title to what the user typed

            # Save the updated resume with all relevant fields
            resume.save()

            # Update user profile flags
            user = request.user
            user.is_applicant = True
            user.has_resume = True
            user.save()

            # Notify the user that their resume has been updated
            notification_message = 'Your resume has been successfully updated.'
            notify_user(user, notification_message, 'resume_update')

            messages.success(request, 'Resume updated successfully.')
            return redirect('update_resume')
        else:
            messages.error(request, f'Form is invalid. Errors: {form.errors}')
    else:
        form = ContactInfoForm(instance=contact_info)

    return render(request, 'resume/update_resume.html', {'form': form})



@login_required
def update_resume_view(request):
    try:
        resume = Resume.objects.get(user=request.user)  # Fetch the resume of the logged-in user
    except Resume.DoesNotExist:
        resume = Resume(user=request.user)  # Create a new resume if it does not exist

    if request.method == "POST":
        form = UpdateResumeForm(request.POST, request.FILES, instance=resume)
        
        if form.is_valid():
            form.save()  # Save the updated resume
            messages.success(request, 'Resume updated successfully.')
            return redirect('user_dashboard')  # Redirect to user dashboard or a success page
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = UpdateResumeForm(instance=resume)  # Pre-populate the form with the resume data

    return render(request, 'resume/update_resume2.html', {'form': form})

def select_category(request):
    """
    Allows applicants to select a category for their skills.
    """
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


@login_required
def selec_skills(request):
    """
    Allows applicants to select skills based on the chosen category.
    """
    if request.method == 'POST':
        selected_category_id = request.session.get('selected_category')
        if selected_category_id:
            selected_category = SkillCategory.objects.get(id=selected_category_id)
            form = SkillForm(request.POST, category=selected_category, user=request.user)  # Pass user parameter
            if form.is_valid():
                resume = Resume.objects.get(user=request.user)
                resume.category = selected_category
                resume.skills.set(form.cleaned_data['skills'])
                resume.save()
                return redirect('onboarding-3')
        else:
            # Handle the case where a category is not selected
            return redirect('select_category')
    else:
        # Handle the case when the request method is not POST
        if request.user.is_applicant:
            selected_category_id = request.session.get('selected_category')
            if selected_category_id:
                selected_category = SkillCategory.objects.get(id=selected_category_id)
                form = SkillForm(category=selected_category, user=request.user)  # Pass user parameter
                return render(request, 'resume/select_skills.html', {'form': form})
            else:
                # Handle the case where a category is not selected
                return redirect('select_category')
        else:
            messages.warning(request, "Permission Denied")
            return redirect('dashboard')



@login_required(login_url='login')
def applicant_onboarding_part3(request):
    """
    Handles the third part of the onboarding process for applicants.
    """
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
    """
    Calculates the match percentage between applicant skills and job requirements.
    """
    common_skills = applicant_skills.intersection(job_skills)
    match_percentage = (len(common_skills) / len(job_skills)) * 100
    return match_percentage, job_skills - common_skills  # Missing skills


def calculate_proximity_percentage(user_location, job_location):
    """
    Calculates the proximity percentage between user and job locations.
    """
    user_coordinates = get_coordinates(user_location)
    job_coordinates = get_coordinates(job_location)
    if user_coordinates and job_coordinates:
        distance_km = geodesic(user_coordinates, job_coordinates).km
        if distance_km <= 50:  # Adjust the proximity threshold as needed
            return 10  # Assign an additional 10% match for jobs within 50 km
    return 0


def get_coordinates(location):
    """
    Retrieves the coordinates for a given location using geocoding.
    """
    try:
        result = geocoder.geocode(location)
        if result:
            latitude = result[0]['geometry']['lat']
            longitude = result[0]['geometry']['lng']
            return latitude, longitude
    except Exception as e:
        print(f"Error retrieving coordinates for {location}: {e}")
    
    return None


def get_matching_jobs(user_job_title, user_skills):
    """
    Retrieves matching jobs based on user job title and skills.
    """
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
    """
    Displays matching jobs for the current user.
    """
    user= request.user
    if user.has_resume:
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
    else:
        messages.info(request,"please create a resume to continue")
        return redirect("update-resume")


def resume_details(request, pk):
    """
    Displays details of a specific resume.
    """
    resume = get_object_or_404(Resume, pk=pk)
    context = {'resume': resume}
    return render(request, 'resume/resume_details.html', context)

