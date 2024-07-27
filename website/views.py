from django.shortcuts import render, redirect
from job.models import Job
# Create your views here.

def job_listing(request):
    jobs = Job.objects.filter(is_available=True)
    context = {'jobs':jobs}
    return render(request, 'website/job_listing.html')