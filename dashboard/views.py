from django.shortcuts import render, redirect
from resume.models import Resume,Education,Experience
from users.models import User
from django.contrib.auth.decorators import login_required
from users.views import login_user
from job.models import Application
@login_required(login_url='login')
def dashboard(request):
    try:
        data = Resume.objects.get(user=request.user)
        user = request.user
        skills = data.skills.all()
        experience = Experience.objects.filter(user = request.user)
        experiences = Experience.objects.all()  # Add this line to retrieve experiences
        educations = Education.objects.all()  # Add this line to retrieve educations
        applications = Application.objects.filter(user = request.user)
    except Resume.DoesNotExist:
        message = "No resume found"
        return render(request, 'dashboard/dashboard.html', {'message': message})
    
    context = {
        'data': data,
        'user': user,
        'skills': skills,
        'experience':experience,
        'experiences': experiences,  # Include experiences in the context
        'educations': educations,  # Include educations in the context
        'applications':applications,
    }
    return render(request, 'dashboard/dashboard.html', context)