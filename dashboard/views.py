from django.shortcuts import render, redirect,get_object_or_404
from resume.models import Resume,Education,ResumeDoc,Experience
from users.models import User
from django.contrib.auth.decorators import login_required
from users.views import login_user
from job.models import Application,calculate_skill_match
import json
from django.core.serializers.json import DjangoJSONEncoder

from resume.models import ContactInfo, WorkExperience, Skill , SkillCategory
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from resume.views import upload_resume
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST


@login_required
def get_suggested_skills(request):
    user = request.user
    job_title = None
    suggested_skills = Skill.objects.none()  # Initialize as an empty QuerySet

    # Get the user's job title
    try:
        resume = Resume.objects.get(user=user)
        job_title = resume.job_title
    except Resume.DoesNotExist:
        job_title = None

    # Filter skills based on the user's job title category
    if job_title:
        try:
            job_category = SkillCategory.objects.get(name=job_title)
            suggested_skills = Skill.objects.filter(categories=job_category)
        except SkillCategory.DoesNotExist:
            suggested_skills = Skill.objects.none()  # Empty QuerySet if category doesn't exist

    suggested_skills_list = list(suggested_skills.values('id', 'name'))
    return JsonResponse(suggested_skills_list, safe=False, encoder=DjangoJSONEncoder)


@require_POST
@csrf_exempt
def update_user_skills(request):
    if request.method == 'POST':
        try:
            selected_skill_ids = request.POST.get('selected_skills', '[]')
            selected_skill_ids = json.loads(selected_skill_ids)
            current_user = request.user

            print("Received POST request to update skills. User:", current_user.username)  # Debug statement

            # Add selected skills without clearing existing ones
            for skill_id in selected_skill_ids:
                skill = Skill.objects.get(id=skill_id)
                current_user.resume.skills.add(skill)

            message = 'Skills updated successfully'
            return redirect('user_dashboard')
        except Exception as e:
            error_message = 'Failed to update skills'
            print(error_message, str(e))  # Debug statement
            return redirect('user_dashboard')
    
    print("Invalid request method or data.")  # Debug statement
    return redirect('user_dashboard')

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import UserLanguageForm,UserProfileForm
from resume.models import UserProfile,UserLanguage
import pycountry
from job.models import Job
from django.db.models import Avg
from dashboard.decorators import resume_required



@login_required(login_url='login')
@resume_required
def dashboard(request):
    try:
        resume = Resume.objects.get(user=request.user)
        contact_info = ContactInfo.objects.get(user=request.user)
        user = request.user
        skills = resume.skills.all()
        work_experiences = WorkExperience.objects.filter(user=request.user)
        educations = Education.objects.filter(user=request.user)
        applications = Application.objects.filter(user=request.user)

        # Set job title to resume category
        job_title = resume.category.name if resume.category else None

        # Filter skills based on the user's job title category
        suggested_skills_json = '[]'  # Default empty JSON array
        if job_title:
            try:
                job_category = SkillCategory.objects.get(name=job_title)
                suggested_skills = Skill.objects.filter(categories=job_category)
                suggested_skills_list = list(suggested_skills.values('id', 'name'))
                suggested_skills_json = json.dumps(suggested_skills_list, cls=DjangoJSONEncoder)
            except SkillCategory.DoesNotExist:
                pass

        # Initialize skills with data from ResumeDoc.extracted_skills
        try:
            resume_doc = ResumeDoc.objects.get(user=request.user)
            extracted_skills = resume_doc.extracted_skills.all()  # Access as queryset

            # Iterate through the queryset and add skills to the resume
            for skill in extracted_skills:
                resume.skills.add(skill)
            
            resume.save()  # Save the updated resume

        except ResumeDoc.DoesNotExist:
            pass

        # Implement pagination for skills
        paginator = Paginator(skills, 10)  # Show 10 skills per page
        page = request.GET.get('page')
        try:
            skills_paginated = paginator.page(page)
        except PageNotAnInteger:
            skills_paginated = paginator.page(1)
        except EmptyPage:
            skills_paginated = paginator.page(paginator.num_pages)

    except Resume.DoesNotExist:
        return redirect('/resume/upload')
    except ContactInfo.DoesNotExist:
        message = "No contact information found"
        return render(request, 'dashboard/dashboard.html', {'message': message})

    jobs = SkillCategory.objects.all()
    
    try:
        user_profile = UserProfile.objects.get(user=request.user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=request.user)
    # Get full country name for display
    country_name = contact_info.country.name if contact_info.country else None
    language_form = UserLanguageForm()
    profile_form = UserProfileForm(instance=user_profile)

    if request.method == 'POST':
        if 'language' in request.POST:
            language_form = UserLanguageForm(request.POST)
            if language_form.is_valid():
                user_language = language_form.save(commit=False)
                user_language.user_profile = user_profile
                user_language.save()
                return redirect('user_dashboard')
        elif 'country' in request.POST:
            profile_form = UserProfileForm(request.POST, instance=user_profile)
            if profile_form.is_valid():
                profile_form.save()
                return redirect('user_dashboard')

    user_languages = UserLanguage.objects.filter(user_profile=user_profile)
    
    top_jobs = Job.objects.order_by('-id')[:5]

    # Calculate matching jobs
    matching_jobs = []
    if user.is_authenticated:
        user_resume_skills = resume.skills.values_list('name', flat=True)
        for job in Job.objects.all():
            job_skills = job.requirements.values_list('name', flat=True)
            match_percentage, _ = calculate_skill_match(user_resume_skills, job_skills)
            if match_percentage >= 10.0:  # Assuming the threshold is 10%
                matching_jobs.append(job)

    context = {
        'contact_info': contact_info,
        'user': user,
        'skills': skills_paginated,  # Use paginated skills
        'work_experiences': work_experiences,
        'educations': educations,
        'applications': applications,
        'suggested_skills_json': suggested_skills_json,
        'jobs': jobs,
        'resume': resume,
        'language_form': language_form,  # Add language form to context
        'profile_form': profile_form,  # Add profile form to context
        'user_profile': user_profile,
        'user_languages': user_languages,
        'country_name': country_name,
        'top_jobs': top_jobs,
        'matching_jobs': matching_jobs,
    }

    return render(request, 'dashboard/dashboard.html', context)

from django.shortcuts import get_object_or_404

@login_required(login_url='login')
def save_job(request):
    if request.method == 'POST':
        job_id = request.POST.get('job')
        print(f"Received job_id: {job_id}")
        if not job_id:
            print("No job_id provided in the POST request.")
            return redirect('user_dashboard')
        
        try:
            job_category = SkillCategory.objects.get(id=job_id)
            job_title = job_category.name
            print(f"Job category found: {job_category.name}")
        except SkillCategory.DoesNotExist:
            print(f"SkillCategory with id {job_id} does not exist.")
            return redirect('user_dashboard')
        
        try:
            resume = Resume.objects.get(user=request.user)
            print(f"Resume found for user {request.user.email}: {resume}")
        except Resume.DoesNotExist:
            print("Resume does not exist for the current user.")
            return redirect('user_dashboard')
        
        # Update and save the resume with both job_title and category
        resume.job_title = job_title
        resume.category = job_category
        resume.save()
        print(f"Resume updated with new job_title: {job_title} and category: {job_category.name}")
    
    return redirect('user_dashboard')

#This view is to delete a selected skill from the resume object
@login_required(login_url='login')
def delete_skill(request, skill_id):
    resume = get_object_or_404(Resume, user=request.user)
    skill = get_object_or_404(Skill, id=skill_id)
    
    if request.method == 'POST':
        resume.skills.remove(skill)
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

from django.template.loader import render_to_string

@login_required(login_url='login')
def paginated_skills(request):
    user = request.user
    resume = Resume.objects.get(user=user)
    skills = resume.skills.all()

    paginator = Paginator(skills, 10)  # Show 10 skills per page
    page = request.GET.get('page')

    try:
        skills_paginated = paginator.page(page)
    except PageNotAnInteger:
        skills_paginated = paginator.page(1)
    except EmptyPage:
        skills_paginated = paginator.page(paginator.num_pages)

    skills_html = render_to_string('partials/skills_list.html', {'skills': skills_paginated})
    pagination_html = render_to_string('partials/pagination.html', {'skills': skills_paginated})

    return JsonResponse({
        'skills_html': skills_html,
        'pagination_html': pagination_html,
    })
    
 
@login_required
def update_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=user_profile)
        if form.is_valid():
            form.save()
            return redirect('user_dashboard')  # Redirect to your desired view after saving
    else:
        form = UserProfileForm(instance=user_profile)

    return render(request, 'dashboard/update_profile.html', {'form': form})

@login_required(login_url='login')
@require_POST
def delete_language(request, language_id):
    try:
        user_language = UserLanguage.objects.get(id=language_id, user_profile__user=request.user)
        user_language.delete()
        return JsonResponse({'success': True})
    except UserLanguage.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Language does not exist'})
    
from django.views.decorators.http import require_POST, require_http_methods
from resume.models import Education
from .forms import EducationForm  # Define this form in forms.py

def save_education(request):
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            education_id = form.cleaned_data.get('id')
            if education_id:
                # Update existing record
                education = get_object_or_404(Education, id=education_id, user=request.user)
                form = EducationForm(request.POST, instance=education)
            else:
                # Create new record
                form.instance.user = request.user  # Set the current user
                form.instance.resume = None  # If you need to set a resume, handle it accordingly

            form.save()
            return redirect('user_dashboard')

        return JsonResponse({'success': False, 'errors': form.errors})

    return JsonResponse({'success': False, 'message': 'Invalid request'})
def delete_education(request, id):
    if request.method == 'DELETE':
        education = get_object_or_404(Education, id=id)
        education.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

def get_education(request, id):
    education = get_object_or_404(Education, id=id)
    data = {
        'institution_name': education.institution_name,
        'degree': education.degree,
        'graduation_year': education.graduation_year,
    }
    return JsonResponse(data)

from resume.models import WorkExperience
from .forms import WorkExperienceForm

def save_experience(request):
    if request.method == 'POST':
        form = WorkExperienceForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                # Save the instance with the user field populated
                experience = form.save(commit=False)
                experience.user = request.user  # Assign the logged-in user
                experience.save()
                return redirect('user_dashboard')
            else:
                return JsonResponse({'error': 'User is not authenticated'}, status=403)
        else:
            return JsonResponse({'errors': form.errors}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def delete_experience(request, id):
    if request.method == 'DELETE':
        experience = get_object_or_404(WorkExperience, id=id, user=request.user)
        experience.delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'error': 'Invalid request method'}, status=405)

def get_experience_details(request, id):
    experience = get_object_or_404(WorkExperience, id=id, user=request.user)
    data = {
        'company_name': experience.company_name,
        'role': experience.role,
        'start_date': experience.start_date.strftime('%Y-%m-%d') if experience.start_date else '',
        'end_date': experience.end_date.strftime('%Y-%m-%d') if experience.end_date else ''
    }
    return JsonResponse(data)