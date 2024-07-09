from django.shortcuts import render, redirect
from resume.models import Resume,Education,Experience
from users.models import User
from django.contrib.auth.decorators import login_required
from users.views import login_user
from job.models import Application
import json
from django.core.serializers.json import DjangoJSONEncoder

from resume.models import ContactInfo, WorkExperience, Skill , SkillCategory
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from resume.views import upload_resume

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
    print("Suggested Skills List:", suggested_skills_list)
    return JsonResponse(suggested_skills_list, safe=False, encoder=DjangoJSONEncoder)

from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
@require_POST
@csrf_exempt
def update_user_skills(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            selected_skill_ids = data.get('selected_skills', [])
            current_user = request.user

            print("Received POST request to update skills. User:", current_user.username)  # Debug statement
            print("Selected Skill IDs:", selected_skill_ids)  # Debug statement

            # Add selected skills without clearing existing ones
            for skill_id in selected_skill_ids:
                skill = Skill.objects.get(id=skill_id)
                current_user.resume.skills.add(skill)

            message = 'Skills updated successfully'
            return redirect('dashboard')
        except Exception as e:
            error_message = 'Failed to update skills'
            print(error_message, str(e))  # Debug statement
            # return JsonResponse({'error': error_message})
            return redirect('dashboard')
    
    # Redirect to dashboard on success or failure
    print("Invalid request method or data.")  # Debug statement
    return redirect('dashboard')

@login_required(login_url='login')
def dashboard(request):
    try:
        resume = Resume.objects.get(user=request.user)
        contact_info = ContactInfo.objects.get(user=request.user)
        user = request.user
        skills = resume.skills.all()
        skills_list = list(skills.values('id','name'))
        skills_json = json.dumps(skills_list, cls=DjangoJSONEncoder)
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

    except Resume.DoesNotExist:
        return redirect('/resume/upload')
    except ContactInfo.DoesNotExist:
        message = "No contact information found"
        return render(request, 'dashboard/dashboard.html', {'message': message})
    
    jobs = SkillCategory.objects.all()
    
    context = {
        'contact_info': contact_info,
        'user': user,
        'skills': skills,
        'work_experiences': work_experiences,
        'educations': educations,
        'applications': applications,
        'suggested_skills_json': suggested_skills_json,
        'skills_json': skills_json,
        'jobs': jobs,
        'resume': resume,
    }

    return render(request, 'dashboard/dashboard.html', context)

@login_required(login_url='login')
def save_job(request):
    if request.method == 'POST':
        job_id = request.POST.get('job')
        try:
            job_category = SkillCategory.objects.get(id=job_id)
            resume = Resume.objects.get(user=request.user)
            resume.category = job_category
            resume.save()
        except SkillCategory.DoesNotExist:
            # Handle the error if the category does not exist
            pass
        except Resume.DoesNotExist:
            # Handle the error if the resume does not exist
            pass
    return redirect('dashboard')