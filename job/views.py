from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from .models import Job, Application
from .forms import CreateJobForm , UpdateJobForm,SkillForm
from resume.views import get_matching_jobs
from django.contrib.auth.decorators import login_required
from onboarding.views import general_knowledge_quiz
from resume.models import Skill,SkillCategory
from job.models import Job,SavedJob
import json
from .jdoodle_api import execute_code
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect, render
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Job, MCQ
from .forms import CreateJobForm
from job.generate_skills import generate_mcqs_for_skill


@login_required(login_url='/login')
def create_job(request):
    if request.method == 'POST':
        form = CreateJobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.user = request.user
            job.company = request.user.company
            job.save()

            # Store the selected category in the session
            request.session['selected_category'] = form.cleaned_data['category'].id
            request.session['selected_job_id'] = job.id

            # Redirect to enter job description
            return redirect('job:enter_job_description')
    else:
        form = CreateJobForm()
    return render(request, 'job/create_job.html', {'form': form})

from .forms import JobDescriptionForm
from django.http import HttpResponseRedirect

def enter_job_description(request):
    if request.method == 'POST':
        form = JobDescriptionForm(request.POST)
        if form.is_valid():
            job_id = request.session.get('selected_job_id')
            job = Job.objects.get(id=job_id)
            job.description = form.cleaned_data['description']
            job.save()

            # Call the function to extract technical skills
            extracted_skills = extract_technical_skills(job.title, job.description)
            print('Extracted skills:', extracted_skills)

            # Add extracted skills to the job
            for skill in extracted_skills:
                skill_obj, created = Skill.objects.get_or_create(name=skill)
                job.extracted_skills.add(skill_obj)

            # Redirect to select_skills view
            return redirect('job:select_skills')
    else:
        form = JobDescriptionForm()
    return render(request, 'job/enter_job_description.html', {'form': form})

import requests

from .job_description_algorithm import extract_technical_skills

from django.contrib.auth.decorators import login_required

@login_required
def select_skills(request):
    if request.user.is_recruiter and request.user.has_company:
        selected_category_id = request.session.get('selected_category')
        selected_job_id = request.session.get('selected_job_id')
        if selected_category_id and selected_job_id:
            selected_category = SkillCategory.objects.get(id=selected_category_id)
            job_instance = Job.objects.get(id=selected_job_id)

            # Retrieve extracted skills for the job instance
            extracted_skills = job_instance.extracted_skills.all()

            if request.method == 'POST':
                form = SkillForm(request.POST, category=selected_category)
                if form.is_valid():
                    job_id = request.session.get('selected_job_id')
                    job = Job.objects.get(id=job_id)
                    job.requirements.set(form.cleaned_data['requirements'])        
                    job.save()

                    entry_level = form.cleaned_data['level']
                    selected_skills = form.cleaned_data['requirements']
                    selected_skill_names = [skill.name for skill in selected_skills]

                    redirect_url = f'/job/generate-questions/?job_title={job_instance.title}&entry_level={entry_level}&selected_skills={",".join(selected_skill_names)}'
                    return redirect(redirect_url)
            else:
                form = SkillForm(category=selected_category, extracted_skills=extracted_skills)

            return render(request, 'job/skill.html', {'form': form, 'extracted_skills': extracted_skills})
        else:
            return redirect('select_category')
    else:
        messages.warning(request, "Permission Denied")
        return redirect('dashboard')



    

@login_required(login_url='/login')
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
    
@login_required(login_url='login')
def confirm_evaluation(request, job_id):
    # Get the job object based on the job_id
    job = Job.objects.get(id=job_id)

    # Create a context dictionary with the data you want to pass to the template
    context = {
        'job': job,
    }

    # Render the confirmation template with the provided context
    return render(request, 'onboarding/confirm.html', context)

@login_required(login_url='login')
def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    # Check if the user has already applied for this job
    existing_application = Application.objects.filter(user=request.user, job=job).first()
    
    # Check if the user has completed the quiz
    application = Application.objects.filter(user=request.user, job=job).first()
    if application and not application.has_completed_quiz:
        existing_application = False
    
    if existing_application:
        # Display a message to the user
        messages.warning(request, "You have already applied for this job.")
        
        # Redirect the user to a specific page (e.g., job details page)
        return redirect('/')
    
    # Set session data to indicate that the user has just applied for the job
    request.session['job_applied'] = True
    request.session['job_id'] = job_id
    
    # Redirect the user to the answer job questions page
    return redirect('job:answer_job_questions', job_id=job_id)




from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Job, MCQ, ApplicantAnswer,SkillQuestion
from .forms import ApplicantAnswerForm

from django.db.models import F

from django.db.models import Q
import random
from django.http import HttpResponseBadRequest

@login_required(login_url='/login')
def answer_job_questions(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    user = request.user

    # Check if the user has already completed all rounds
    application, created = Application.objects.get_or_create(user=user, job=job)
    if application.has_completed_quiz:
        messages.warning(request, "You have already completed the quiz for this job.")
        return redirect('job:job_application_success')  # Redirect to success page or any other destination

    # Determine the current round based on completion status
    if not application.round1_completed:
        round_number = 1
    elif not application.round2_completed:
        round_number = 2
    elif not application.round3_completed:
        round_number = 3
    else:
        # All rounds completed, update quiz_score and redirect to success page
        application.quiz_score = application.round1_score + application.round2_score + application.round3_score
        application.has_completed_quiz = True
        application.save()
        messages.success(request, "Congratulations! You have completed all rounds.")
        return redirect('job:job_application_success')

    # Calculate the number of questions per round
    total_questions = SkillQuestion.objects.filter(skill__in=job.requirements.all(), entry_level=job.level).count()
    questions_per_round = total_questions // 3

    # Calculate the starting and ending indices for the current round
    start_index = (round_number - 1) * questions_per_round
    end_index = min(round_number * questions_per_round, total_questions)

    if request.method == 'POST':
        answers = request.POST
        if answers:
            total_score = 0  # Initialize total score
            for mcq in SkillQuestion.objects.filter(skill__in=job.requirements.all(), entry_level=job.level)[start_index:end_index]:
                answer = answers.get(f'question{mcq.id}')
                if answer:
                    applicant_answer = ApplicantAnswer.objects.create(
                        applicant=user,
                        question=mcq,
                        answer=answer,
                        job=job
                    )
                    applicant_answer.calculate_score()  # Calculate score for each answer
                    total_score += applicant_answer.score  # Update total score
            
            # Include extracted skills in calculating the score
            for skill in job.extracted_skills.all():
                # Fetch questions related to each extracted skill
                skill_questions = SkillQuestion.objects.filter(skill=skill, entry_level=job.level)
                for mcq in skill_questions:
                    answer = answers.get(f'question{mcq.id}')
                    if answer:
                        applicant_answer = ApplicantAnswer.objects.create(
                            applicant=user,
                            question=mcq,
                            answer=answer,
                            job=job
                        )
                        applicant_answer.calculate_score()  # Calculate score for each answer
                        total_score += applicant_answer.score  # Update total score

            # Update round completion status and total score
            if round_number == 1:
                application.round1_completed = True
                application.round1_score = total_score
            elif round_number == 2:
                application.round2_completed = True
                application.round2_score = total_score
            elif round_number == 3:
                application.round3_completed = True
                application.round3_score = total_score
            application.save()

            # Calculate quiz score based on completed rounds
            application.quiz_score = application.round1_score + application.round2_score + application.round3_score
            application.save()

            messages.success(request, f"Your answers for round {round_number} have been recorded. Total score: {total_score}")
            
            # Redirect to a page indicating the start of the next round
            if round_number <= 2:
                # Render the round start template for the next round
                return render(request, 'job/rounds/round_start.html', {'round_number': round_number + 1})
            else:
                # For round 3, redirect to the next step directly
                return redirect('job:answer_job_questions', job_id=job_id)
        else:
            messages.error(request, "Please answer all questions.")
            return redirect('job:answer_job_questions', job_id=job_id)
    else:
        # Fetch questions for the current round
        mcqs = SkillQuestion.objects.filter(skill__in=job.requirements.all(), entry_level=job.level)[start_index:end_index]

        # Include extracted skills questions for the current round
        extracted_skills_questions = []
        for skill in job.extracted_skills.all():
            extracted_skill_questions = SkillQuestion.objects.filter(skill=skill, entry_level=job.level)
            extracted_skills_questions.extend(extracted_skill_questions)

        # Total Selected Questions
        print("Total Selected Questions:", mcqs.count() + len(extracted_skills_questions))  # Print the count of selected questions
        context = {
            'job': job,
            'mcqs': mcqs,
            'extracted_skills_questions': extracted_skills_questions,
            'round_number': round_number,
        }
        
        if round_number == 1:
            template_name = 'job/rounds/round1.html'
        elif round_number == 2:
            template_name = 'job/rounds/round2.html'
        elif round_number == 3:
            template_name = 'job/rounds/round3.html'
        else:
            # Handle invalid round number
            return HttpResponseBadRequest("Invalid round number")

        return render(request, template_name, context)


@login_required(login_url='/login')
def job_application_success(request):
    # Retrieve skill scores from session
    skill_scores = request.session.get('skill_scores', {})

    context = {
        'skill_scores': skill_scores,
    }
    return render(request, 'job/application_success.html', context)



def save_job(request, job_id):
    """
    Save a job for later viewing.
    """
    job = get_object_or_404(Job, pk=job_id)

    if request.method == 'POST':
        if 'submit' in request.POST:
            print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
            saved_job, created = SavedJob.objects.get_or_create(user=request.user, job=job)
            if created:
                saved_job.save()
                
                messages.success(request, "Job saved successfully.")
            else:
                
                messages.info(request, "You have already saved this job.")

    # Redirect the user back to the job details page
    return redirect('job:view_saved_jobs')

def view_saved_jobs(request):
    """
    View the list of saved jobs.
    """
    saved_jobs = SavedJob.objects.filter(user=request.user)
    return render(request, 'job/saved_jobs.html', {'saved_jobs': saved_jobs})

def delete_saved_job(request, saved_job_id):
    """
    Delete a saved job.
    """
    saved_job = get_object_or_404(SavedJob, pk=saved_job_id, user=request.user)
    if request.method == 'POST':
        saved_job.delete()
        return redirect('view_saved_jobs')
    return render(request, 'job/delete_saved_job.html', {'saved_job': saved_job})



''' COmpiler integration with Jdoodler '''

@login_required(login_url='/login')
def run_code(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        script = data.get('script')
        language = data.get('language')
        version_index = data.get('version_index')
        user = request.user
        output = execute_code(script, language, version_index)

        # Check if output is a dictionary or a string
        if "Error occurred" in output:
            response_data = {'output': output}
        else:
            output_dict = json.loads(output)
            response_data = {'output': output_dict.get('output')}

        print(response_data['output'])
        return JsonResponse(response_data)

    # Handle other request methods (e.g., GET) if needed
    return render(request, "job/compiler/run_code.html")

    # Return an error response for disallowed methods
    return HttpResponseNotAllowed(['POST'])

def job_details(request):
    return render(request, "job/job_details.html")

def success_page(request):
    return render(request, "job/compiler/success.html")

def fail_page(request):
    return render(request, "job/compiler/fail.html")