from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from .models import Job, Application
from .forms import CreateJobForm , UpdateJobForm
from resume.views import get_matching_jobs



# create a job
def create_job(request):
    if request.user.is_recruiter and request.user.has_company:
        if request.method == 'POST':
            form = CreateJobForm(request.POST)
            if form.is_valid():
                var = form.save(commit=False)
                var.user = request.user
                var.company = request.user.company
                var.save()
                messages.info(request,"New job has been created")
                return redirect('dashboard')
            else:
                messages.warning(request,'Something went wrong ')
                return redirect('create_job')
        else:
            form = CreateJobForm()
            context = {'form':form}
            return render(request, 'job/create_job.html',context)
        
    else:
        messages.warning(request,'Permission Denied!')
        return redirect('dashboard')
    

def update_job(request,pk):
    job = Job.objects.get(pk=pk)
    if request.method == 'POST':
        form = UpdateJobForm(request.POST, instance=job)
        if form.valid():
            form.save()
            messages.info(request,"Job info has been Updated")
            return redirect('dashboard')
        else:
            messages.warning(request,'Something went wrong ')
    else:
        form = UpdateJobForm()
        context = {'form':form}
        return render(request, 'job/update_job.html',context)
    
from onboarding.views import general_knowledge_quiz
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    # Check if the user has already applied for this job
    existing_application = Application.objects.filter(user=request.user, job=job).first()
    
    if existing_application:
        # Display a message to the user
        messages.warning(request, "You have already applied for this job.")
        
        # Redirect the user to a specific page (e.g., job details page)
        # return redirect('get_matching_jobs', job_id=job_id)
        return redirect('/')
    
    # Create a new instance of the Application model
    application = Application(user=request.user, job=job)
    
    # Save the application
    application.save()
    context = {'job',job}
    # Redirect to a success page or perform other actions
    return redirect('general_knowledge_quiz')