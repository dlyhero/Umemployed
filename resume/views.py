from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Resume, SkillCategory, Skill
from .forms import UpdateResumeForm, UpdateResumeForm2, UpdateResumeForm3
from users.models import User
from job.models import Job

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
                return redirect('onboarding-2')
            else:
                messages.warning(request, 'Something went wrong')
        else:
            form = UpdateResumeForm(instance=resume)

        context = {'form': form}
        return render(request, 'resume/update_resume.html', context)
    else:
        messages.warning(request, "Permission Denied")
        return redirect('dashboard')

def applicant_onboarding_part2(request):
    if request.user.is_applicant:
        resume = get_object_or_404(Resume, user=request.user)

        if request.method == 'POST':
            form = UpdateResumeForm2(request.POST, request.FILES, instance=resume)
            if form.is_valid():
                # Save the resume info
                form.save()

                # Process the selected skill category and skills
                category_id = request.POST.get('category')
                skills_ids = request.POST.getlist('skills')

                category = SkillCategory.objects.get(id=category_id)
                skills = Skill.objects.filter(id__in=skills_ids)

                # Update the resume with the selected category and skills
                resume.category = category
                resume.skills.set(skills)
                resume.save()

                messages.info(request, 'Your resume information has been updated.')
                return redirect('onboarding-3')
            else:
                messages.warning(request, 'Something went wrong')
        else:
            form = UpdateResumeForm2(instance=resume)

        # Retrieve the available skill categories for the form
        skill_categories = SkillCategory.objects.all()

        context = {
            'form': form,
            'skill_categories': skill_categories,
        }
        return render(request, 'resume/applicant_onboarding_part2.html', context)
    else:
        messages.warning(request, "Permission Denied")
        return redirect('dashboard')

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
            'title': job.title,
            'location': job.location,
            'is_available': job.is_available,
            'salary': job.salary,
            'match_percentage': match_percentage,
            'missing_skills': list(missing_skills)  # Convert set to list for iteration in HTML
        }
        matching_jobs.append(job_dict)

    context = {'matching_jobs': matching_jobs}
    return render(request, 'job/matching_jobs.html', context)


def get_matching_jobs(user_job_title, user_skills):
    job_by_title = Job.objects.filter(title__icontains=user_job_title)
    matching_jobs = []

    for job in job_by_title:
        job_skills = set(job.requirements.all())
        match_percentage, missing_skills = calculate_skill_match(user_skills, job_skills)
        matching_jobs.append({'job': job, 'match_percentage': match_percentage, 'missing_skills': missing_skills})

    return matching_jobs

















def resume_details(request, pk):
    resume = get_object_or_404(Resume, pk=pk)
    context = {'resume': resume}
    return render(request, 'resume/resume_details.html', context)