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
from django.http import JsonResponse

def update_user_skills(request):
    if request.method == 'POST':
        try:
            # Parse JSON data from the request body
            data = json.loads(request.body.decode('utf-8'))
            selected_skill_ids = data.get('selected_skills', [])
            print("Received Skill IDs:", selected_skill_ids)  # Debug statement

            current_user = request.user
            print("Current User:", current_user)  # Debug statement

            # Clear existing skills
            current_user.resume.skills.clear()
            print("Existing skills cleared.")  # Debug statement

            # Add selected skills
            current_user.resume.skills.add(*selected_skill_ids)
            print("Selected skills added.")  # Debug statement

            message = 'Skills updated successfully'
            return JsonResponse({'message': message})
        except Exception as e:
            print("Error updating skills:", str(e))  # Debug statement
            return JsonResponse({'error': 'Failed to update skills'})

    return JsonResponse({'error': 'Invalid request'})


@login_required(login_url='login')
def dashboard(request):
    resume = Resume.objects.filter(user = request.user)
    if not resume.exists():
        return redirect('/resume/upload')
    try:
        contact_info = ContactInfo.objects.get(user=request.user)
        user = request.user
        resume = Resume.objects.get(user=user)
        skills = resume.skills.all()
        skills_list = list(skills.values('id','name'))
        skills_json = json.dumps(skills_list, cls=DjangoJSONEncoder)
        work_experiences = WorkExperience.objects.filter(user=request.user)
        educations = Education.objects.filter(user=request.user)
        applications = Application.objects.filter(user=request.user)
        
        # Get the user's job title
        try:
            resume = Resume.objects.get(user=request.user)
            job_title = resume.job_title
        except Resume.DoesNotExist:
            job_title = None

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

    except ContactInfo.DoesNotExist:
        message = "No contact information found"
        return render(request, 'dashboard/dashboard.html', {'message': message})
    
    context = {
        'contact_info': contact_info,
        'user': user,
        'skills': skills,
        'work_experiences': work_experiences,
        'educations': educations,
        'applications': applications,
        'suggested_skills_json': suggested_skills_json,
        'skills_json':skills_json,
    }
    print("SKILLS::::", skills)

    return render(request, 'dashboard/dashboard.html', context)