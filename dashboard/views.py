from django.shortcuts import render, redirect
from resume.models import Resume
from users.models import User

def dashboard(request):
    try:
        data = Resume.objects.get(user=request.user)
        user = request.user
    except Resume.DoesNotExist:
        message = "No resume found"
        return render(request, 'dashboard/dashboard.html', {'message': message})
    
    context = {'data': data, 'user': user}
    return render(request, 'dashboard/dashboard.html', context)