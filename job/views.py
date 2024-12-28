from django.shortcuts import render,redirect,get_object_or_404
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
from .models import Job, MCQ
from .forms import CreateJobForm
from django.http import JsonResponse
from .models import Skill, SkillQuestion, CompletedSkills
from .forms import JobDescriptionForm
from django.http import HttpResponseRedirect
import requests
from .job_description_algorithm import extract_technical_skills
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import Job, MCQ, ApplicantAnswer,SkillQuestion,Shortlist,RetakeRequest
from .forms import ApplicantAnswerForm
from django.db.models import F
from django.db.models import Q
import random
from django.http import HttpResponseBadRequest
from .models import ApplicantAnswer
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Job, Application, SkillQuestion, ApplicantAnswer

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Application, SkillQuestion, ApplicantAnswer, CompletedSkills, Job, Skill
from .forms import ApplicantAnswerForm  # Make sure this form is updated as necessary
from .forms import JobDescriptionForm

from .tasks import send_new_job_email_task, send_recruiter_job_confirmation_email_task
from notifications.utils import notify_user
from django.core.mail import send_mail
from notifications.utils import notify_user_declined
from django.conf import settings
from notifications.models import Notification


import json
import logging

from django.http import JsonResponse

logger = logging.getLogger(__name__)

from django.http import JsonResponse
import json
from users.models import User
from users.email_tasks import send_new_job_email,send_application_email

@login_required(login_url='/login')
def create_job(request):
    user = request.user
    company=request.user.company
    if request.method == 'POST':
        form = CreateJobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.user = request.user
            job.company = request.user.company
            job.save()

            # Optionally store job ID in session or context for further steps
            request.session['selected_job_id'] = job.id

            # Redirect to success page or next step
            return redirect('job:job_type_view')  # Adjust this as needed
        else:
            # Handle form errors if needed
            print(form.errors)
    else:
        form = CreateJobForm()

    return render(request, 'dashboard/recruiterDashboard/addJob.html', {'form': form, 'company':company})


from .forms import JobTypeForm

@login_required(login_url='/login')
def job_type_view(request):
    user = request.user
    company = user.company

    if request.method == 'POST':
        form = JobTypeForm(request.POST)
        if form.is_valid():
            job_id = request.session.get('selected_job_id')
            job = get_object_or_404(Job, id=job_id)
            job.job_type = request.POST.get('job_types', '')
            job.experience_levels = request.POST.get('experience_levels', '')
            job.weekly_ranges = request.POST.get('weekly_ranges', '')
            job.shifts = request.POST.get('shifts', '')
            job.save()
            messages.success(request, "Job preferences updated successfully.")
            return redirect('job:enter_job_description')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = JobTypeForm()

    return render(request, 'dashboard/recruiterDashboard/jobProps.html', {'form': form, 'company': company})


@login_required
def enter_job_description(request):
    user = request.user
    company = user.company

    if request.method == 'POST':
        form = JobDescriptionForm(request.POST)
        if form.is_valid():
            job_id = request.session.get('selected_job_id')
            if not job_id:
                messages.error(request, "Job ID not found in session.")
                return redirect('dashboard')

            job = get_object_or_404(Job, id=job_id)
            description = form.cleaned_data['description']
            responsibilities = form.cleaned_data['responsibilities']
            ideal_candidate = form.cleaned_data['ideal_candidate']
            
            # Check if the description is at least 20 words long
            if len(description.split()) < 20:
                messages.error(request, "The job description must be at least 20 words long.")
                return redirect('job:enter_job_description')

            # Update the job fields
            job.description = description
            job.responsibilities = responsibilities
            job.ideal_candidate = ideal_candidate
            job.save()

            # Combine the job title with the description, responsibilities, and ideal_candidate
            combined_text = (
                (description or '') +
                (responsibilities or '') +
                (ideal_candidate or '')
            )
            extracted_skills = extract_technical_skills(job.title, combined_text)
            print('Extracted skills:', extracted_skills)

            # Add extracted skills to the job
            for skill in extracted_skills:
                skill_obj, created = Skill.objects.get_or_create(name=skill)
                job.extracted_skills.add(skill_obj)

            # Ensure session data
            request.session['selected_job_id'] = job.id
            request.session['selected_category'] = job.category.id  # Assuming job has a category field

            # Redirect to select_skills view
            print("Redirecting to select_skills")
            return redirect('job:select_skills')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = JobDescriptionForm()
    
    return render(request, 'dashboard/recruiterDashboard/jobDescription.html', {'form': form, 'company': company})


from django.shortcuts import get_object_or_404


@login_required
def select_skills(request):
    company = request.user.company
    if request.user.is_recruiter and request.user.has_company:
        selected_category_id = request.session.get('selected_category')
        selected_job_id = request.session.get('selected_job_id')

        if selected_category_id and selected_job_id:
            try:
                selected_category = SkillCategory.objects.get(id=selected_category_id)
                job_instance = Job.objects.get(id=selected_job_id)

                # Retrieve extracted skills for the job instance
                extracted_skills = job_instance.extracted_skills.all()

                if request.method == 'POST':
                    form = SkillForm(request.POST, job_instance=job_instance)
                    if form.is_valid():
                        selected_extracted_skills = form.cleaned_data['extracted_skills']
                        job_instance.extracted_skills.set(selected_extracted_skills)

                        # Also add selected extracted skills to requirements
                        job_instance.requirements.set(selected_extracted_skills)

                        # Set the job level
                        job_instance.level = form.cleaned_data['level']
                        job_instance.save()

                        # Send new job email notification
                        job_description = job_instance.description if job_instance.description else 'No description available.'
                        job_link = request.build_absolute_uri(job_instance.get_absolute_url())
                        
                        # Schedule email sending task with a 2-minute delay
                        users = User.objects.filter(skills__in=selected_extracted_skills).distinct()
                        print(f"Users found with matching skills: {[user.email for user in users]}")
                        for user in users:
                            send_new_job_email_task.apply_async(
                                args=[user.email, user.get_full_name(), job_instance.title, job_link, job_description, company.name, job_instance.id],
                                countdown=120  # 2 minutes delay
                            )

                        # Notify all users about the new job
                        message = f"A new job has been posted: {job_instance.title}. Check it out!"
                        notification_type = 'new_job_posted'
                        
                        # Fetch users with matching skills
                        for u in users:
                            notify_user(u, message, notification_type)
                            
                        # Notify the recruiter about the job creation
                        recruiter_email = request.user.email
                        send_recruiter_job_confirmation_email_task.apply_async(
                            args=[recruiter_email, request.user.get_full_name(), job_instance.title, company.name, job_instance.id],
                            countdown=120  # 2 minutes delay
                        )

                        # Redirect to the next phase (e.g., generate questions)
                        entry_level = form.cleaned_data['level']
                        selected_skill_names = [skill.name for skill in selected_extracted_skills]
                        redirect_url = f'/job/generate-questions/?job_title={job_instance.title}&entry_level={entry_level}&selected_skills={",".join(selected_skill_names)}'
                        messages.info(request, "Your job has been successfully created, please be patient while we process the job assessment!")
                        return redirect(redirect_url)
                else:
                    form = SkillForm(job_instance=job_instance)

                return render(request, 'dashboard/recruiterDashboard/selectSkills.html', {
                    'form': form,
                    'extracted_skills': extracted_skills,
                    'company': company,
                })
            except SkillCategory.DoesNotExist:
                messages.error(request, "Selected category not found.")
                return redirect('job:select_category')
            except Job.DoesNotExist:
                messages.error(request, "Selected job not found.")
                return redirect('job:select_category')
        else:
            messages.error(request, "Session data missing for selected category or job.")
            return redirect('job:select_category')
    else:
        messages.warning(request, "Permission Denied")
        return redirect('dashboard')



from .forms import JobUpdateForm

from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.urls import reverse
import logging

@login_required
def update_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    company = job.company

    if request.method == 'POST':
        form = JobUpdateForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            return redirect('view_my_jobs', company.id)
    else:
        form = JobUpdateForm(instance=job)

    return render(request, 'job/update_job.html', {'form': form, 'job': job, 'company': company})



    
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

# Configure logging
logger = logging.getLogger(__name__)



from django.db import transaction

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Job, Application, CompletedSkills, SkillQuestion, ApplicantAnswer
import logging

logger = logging.getLogger(__name__)

@login_required(login_url='/login')
def answer_job_questions(request, job_id):
    # Fetch the job and user
    job = get_object_or_404(Job, id=job_id)
    user = request.user
    skills = job.requirements.all()
    last_skill = skills.last()  # Get the last skill based on the current ordering
    last_skill_id = last_skill.id if last_skill else None

    # Get or create an application instance
    application, created = Application.objects.get_or_create(user=user, job=job)

    # Check if the user has already accessed this view
    if application.has_started:
        messages.warning(request, "You have already attempted the application for this job. Please contact the admins if you need further assistance.")
        return redirect('job:report_test', job_id=job_id)

    # Mark the application as started
    application.has_started = True
    application.save()

    # Check if the quiz has already been completed
    if application.has_completed_quiz:
        messages.warning(request, "You have already completed the quiz for this job.")
        return redirect('job:job_application_success', job_id=job_id)

    # Determine the remaining skills and current skill
    completed_skills = CompletedSkills.objects.filter(user=user, job=job, is_completed=True).values_list('skill_id', flat=True)
    remaining_skills = [skill for skill in skills if skill.id not in completed_skills]
    logger.debug(f"Remaining skills: {remaining_skills}")

    if not remaining_skills:
        # All skills have been completed
        application.has_completed_quiz = True
        application.save()
        messages.success(request, "Congratulations! You have completed all rounds.")
        return redirect('job:job_application_success', job_id=job_id)

    # Get the current skill to be answered
    current_skill = remaining_skills[0]
    logger.debug(f"Current skill: {current_skill}")

    if request.method == 'POST':
        # Process form submission
        answers = request.POST
        logger.debug(f"POST data: {answers}")

        if answers:
            total_score = 0
            mcqs = SkillQuestion.objects.filter(skill=current_skill, entry_level=job.level)
            logger.debug(f"MCQs for skill {current_skill}: {mcqs}")

            existing_answers = set(ApplicantAnswer.objects.filter(
                applicant=user,
                job=job,
                application=application,
                question__in=mcqs
            ).values_list('question_id', flat=True))

            with transaction.atomic():
                for mcq in mcqs:
                    answer = answers.get(f'question{mcq.id}')
                    if answer and mcq.id not in existing_answers:
                        applicant_answer = ApplicantAnswer.objects.create(
                            applicant=user,
                            question=mcq,
                            answer=answer,
                            job=job,
                            application=application
                        )
                        applicant_answer.calculate_score()
                        total_score += applicant_answer.score

                application.round_scores[str(current_skill.id)] = total_score
                application.save()

                # Update or create CompletedSkills entry
                CompletedSkills.objects.update_or_create(
                    user=user,
                    job=job,
                    skill=current_skill,
                    defaults={'is_completed': True}
                )

            logger.debug(f"Updated round_scores: {application.round_scores}")

            messages.success(request, f"Your answers for the skill '{current_skill.name}' have been recorded. Total score: {total_score}")
            return redirect('job:job_application_success', job_id=job_id)
        else:
            messages.error(request, "Please answer all questions.")
            return redirect('job:answer_job_questions', job_id=job_id)

    else:
        # Render the quiz form
        mcqs = SkillQuestion.objects.filter(
            Q(skill=current_skill) & Q(entry_level=job.level) &
            ~Q(option_a='') & ~Q(option_b='') & ~Q(option_c='') & ~Q(option_d='')
        ).order_by('?')[:5]  # Randomize and limit to 5 questions
        logger.debug(f"Current skill questions: {mcqs}")

        # Check if there are questions to render
        if not mcqs:
            logger.error(f"No questions found for skill: {current_skill}")
            messages.error(request, "No questions available for the current skill.")
            return redirect('job:job_application_success', job_id=job_id)

        # Print the questions to debug
        for question in mcqs:
            logger.debug(f"Question ID: {question.id}, Question: {question.question}, Options: {question.option_a}, {question.option_b}, {question.option_c}, {question.option_d}")

        context = {
            'job': job,
            'mcqs': mcqs,
            'current_skill': current_skill,
            'skills': skills,
            'job_id': job.id,
            'last_skill_id': last_skill_id,
        }

        return render(request, 'job/rounds/round1.html', context)
    
@login_required(login_url='/login')
def report_test(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.method == 'POST':
        reason = request.POST.get('reason')
        retake_request = RetakeRequest.objects.create(user=request.user, job=job, reason=reason)

        # Send email to superusers
        superusers = User.objects.filter(is_superuser=True)
        superuser_emails = [user.email for user in superusers]
        send_mail(
            'New Retake Request',
            f'User {request.user.username} has requested to retake the test for job {job.id}.\n\nReason:\n{reason}',
            'Assessment-Issue',
            superuser_emails,
            fail_silently=False,
        )

        return redirect('home')

    context = {'job': job}
    return render(request, 'job/request_retake.html', context)



from django.core.files.storage import default_storage
from django.views.decorators.csrf import csrf_exempt

def save_video(request):
    if request.method == 'POST' and request.FILES.get('video') and request.POST.get('application_id'):
        video = request.FILES['video']
        application_id = request.POST.get('application_id')
        try:
            application = Application.objects.get(id=application_id)
            file_path = default_storage.save(f'videos/{video.name}', video)
            application.video_file = file_path
            application.save()
            print(f'Video saved for application {application_id} at {file_path}')  # Debugging log
            return JsonResponse({'success': True, 'file_path': file_path})
        except Application.DoesNotExist:
            print(f'Application {application_id} not found')  # Debugging log
            return JsonResponse({'success': False, 'error': 'Application not found'})
    print('Invalid request')  # Debugging log
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required(login_url='/login')  
def get_questions_for_skill(request, skill_id):  
    user = request.user  # Assuming user is authenticated  

    # Fetch skill based on skill_id  
    skill = get_object_or_404(Skill, id=skill_id)  
    print(f"Skill fetched: {skill.name}")  # Print the name of the fetched skill  

    # Fetch job_id from query parameters  
    job_id = request.GET.get('job_id')  
    if not job_id:  
        return JsonResponse({'error': 'job_id parameter is missing'}, status=400)  

    # Fetch job based on job_id  
    job = get_object_or_404(Job, id=job_id)  
    print(f"Job fetched: {job.title}")  # Print the title of the fetched job  

    # Check if there's an application for the specified job and user  
    try:  
        current_application = Application.objects.get(user=user, job=job, has_completed_quiz=False)  
        print(f"Current application found for job: {job.title}")  # Log successful application retrieval  
    except Application.DoesNotExist:  
        return JsonResponse({'error': 'No active job application found for this job'}, status=400)  

    # Check if the user has completed this skill for the current job  
    completed_skills = CompletedSkills.objects.filter(user=user, job=job, skill=skill).exists()  

    # If the skill is already completed for this job, return empty questions list  
    if completed_skills:  
        print(f"User has already completed skill: {skill.name} for job: {job.title}")  # Log completion  
        return JsonResponse({'questions': [], 'message': 'You have already completed this skill for the current job.'})  

    # Fetch questions for the specified skill and entry level, excluding those with any empty options  
    questions = SkillQuestion.objects.filter(  
        Q(skill=skill) & Q(entry_level=job.level) &  
        ~Q(option_a='') & ~Q(option_b='') & ~Q(option_c='') & ~Q(option_d='')  
    ).order_by('?')[:5]  # Randomize and limit to 5 questions  

    # Log the number of questions fetched  
    print(f"Number of questions fetched for skill {skill.name}: {questions.count()}")  

    # Serialize questions data  
    serialized_questions = [  
        {  
            'id': q.id,  
            'question': q.question,  
            'options': [q.option_a, q.option_b, q.option_c, q.option_d]  
        }  
        for q in questions  
    ]  

    # Log the serialized questions  
    for question in serialized_questions:  
        print(f"Question ID: {question['id']}, Question: {question['question']}, Options: {question['options']}")  

    return JsonResponse({'questions': serialized_questions})  


@login_required(login_url='/login')
def save_responses(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            responses = data.get('responses', [])
            skill_id = data.get('skill_id')
            job_id = data.get('job_id')  # Fetch the job_id from request data

            if not skill_id:
                raise ValueError("Skill ID not provided in the request data.")
            
            if not job_id:
                raise ValueError("Job ID not provided in the request data.")
            
            # Fetch job based on job_id
            job = get_object_or_404(Job, id=job_id)

            # Fetch the application for the specified job and user
            try:
                current_application = Application.objects.get(user=request.user, job=job, has_completed_quiz=False)
            except Application.DoesNotExist:
                return JsonResponse({'error': 'No active job application found for this job'}, status=400)

            total_score = 0
            
            for response in responses:
                question_id = response.get('question_id')
                answer = response.get('answer')
                
                # Log received data
                logger.debug(f"Processing question {question_id} with answer {answer}")
                
                if not question_id or not answer:
                    logger.error("Question ID or answer missing in the response data.")
                    continue  # Skip to the next response
                
                # Fetch SkillQuestion by question_id
                try:
                    question = SkillQuestion.objects.get(id=question_id)
                except SkillQuestion.DoesNotExist:
                    logger.error(f"SkillQuestion with ID {question_id} does not exist.")
                    continue  # Skip to the next response
                
                # Save ApplicantAnswer instance
                applicant_answer = ApplicantAnswer(
                    applicant=request.user,
                    question=question,
                    answer=answer,
                    job=job,
                    application=current_application  # Set the application field
                )
                applicant_answer.calculate_score()
                total_score += applicant_answer.score
                
                # Save the instance to the database
                applicant_answer.save()

            # Update the round_scores for the current skill
            current_application.round_scores[str(skill_id)] = total_score
            current_application.save()  # Save here to update the round_scores

            # Recalculate the quiz score and other related fields
            current_application.update_quiz_score()
            current_application.update_matching_percentage()
            current_application.update_total_scores()
            current_application.save()  # Save the updated fields

            # Check if the quiz is completed and update the flag
            current_application.has_completed_quiz = current_application.is_quiz_completed()
            current_application.save()

            return JsonResponse({'success': True, 'total_score': total_score})

        except ValueError as e:
            logger.error(f"ValueError: {str(e)}")
            return JsonResponse({'success': False, 'error': str(e)}, status=400)
        except json.JSONDecodeError as e:
            logger.error(f"JSONDecodeError: {str(e)}")
            return JsonResponse({'success': False, 'error': 'Invalid JSON in request body'}, status=400)
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return JsonResponse({'success': False, 'error': 'An unexpected error occurred'}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


    
@login_required(login_url='/login')
def job_application_success(request, job_id):
    # Retrieve the job object
    try:
        job = Job.objects.get(id=job_id)
    except Job.DoesNotExist:
        messages.error(request, "Job not found.")
        return redirect('job:job_list')  # Adjust this as needed

    # Retrieve skill scores from session
    skill_scores = request.session.get('skill_scores', {})

    # Create or update the application object
    application, created = Application.objects.update_or_create(
        user=request.user,
        job=job,
        defaults={
            'quiz_score': request.session.get('quiz_score', 0),  # Assuming quiz_score is stored in session
            'matching_percentage': request.session.get('matching_percentage', 0.0),  # Assuming matching percentage is stored in session
            'overall_match_percentage': request.session.get('overall_match_percentage', 0.0),  # Assuming overall matching percentage is stored in session
        }
    )

    # Notify the job poster (recruiter) about the new application
    if job.user:  # Assuming job.user is the recruiter
        recruiter = job.user
        recruiter_message = f"A new application has been received for the job: {job.title}."
        notify_user(recruiter, recruiter_message, 'job_application')

        # Construct the job link with company and job IDs
        job_link = request.build_absolute_uri(
            reverse('job_applications', args=[job.company.id, job.id])
        )

        # Send an email to the recruiter about the new application
        send_application_email(recruiter.email, request.user.get_full_name(), job.title, job_link)

    # Retrieve all applications for the job
    applications = Application.objects.filter(job=job)

    # Calculate overall match percentage for each application
    for app in applications:
        total_questions = SkillQuestion.objects.filter(skill__in=job.requirements.all(), entry_level=job.level).count()
        if total_questions > 0:
            app.overall_match_percentage = (app.quiz_score / total_questions) * 100
        else:
            app.overall_match_percentage = 0.0
        app.save()

    # Sort applications based on quiz score, matching percentage, and randomly if there's a tie
    applications = sorted(applications, key=lambda x: (x.quiz_score, x.matching_percentage, random.random()), reverse=True)

    # Determine if the current user's application is in the top 5 or the next 5 (waiting list)
    top_5_applications = applications[:5]
    waiting_list_applications = applications[5:10]

    # Construct the job link for applicant emails
    job_link = request.build_absolute_uri(
        reverse('job_applications', args=[job.company.id, job.id])
    )

    if application in top_5_applications:
        applicant_message = f"Your application for the job '{job.title}' has been received and you are in the top 5 candidates. Please wait for further updates."
        notify_user(request.user, applicant_message, 'application_received')
        send_application_email(request.user.email, "Application Received", applicant_message, job_link)
    elif application in waiting_list_applications:
        applicant_message = f"Your application for the job '{job.title}' has been received and you are on the waiting list. Please wait for further updates."
        notify_user(request.user, applicant_message, 'application_received')
        send_application_email(request.user.email, "Application Received", applicant_message, job_link)
    else:
        applicant_message = f"Your application for the job '{job.title}' has been received. Unfortunately, you did not make it to the top 10 candidates."
        notify_user(request.user, applicant_message, 'application_received')
        send_application_email(request.user.email, "Application Received", applicant_message, job_link)

    # Check if any waiting list applications have been replaced
    for app in waiting_list_applications:
        if app != application and app not in applications[:10]:
            rejection_message = f"Your application for the job '{job.title}' has been rejected as you have been replaced by another candidate."
            notify_user(app.user, rejection_message, 'application_rejected')
            send_application_email(app.user.email, "Application Rejected", rejection_message, job_link)

    context = {
        'skill_scores': skill_scores,
        'job': job,
        'application': application,
    }
    return render(request, 'job/application_success.html', context)

def evaluation_results(request,job_id):
    job = Job.objects.get(id=job_id)
    context = {
        'job':job,
    }
    return render(request, "job/evaluation_results.html",context)



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
    if request.method == 'POST' and request.user.is_authenticated:
        saved_job = get_object_or_404(SavedJob, pk=saved_job_id, user=request.user)

        # Delete the saved job
        saved_job.delete()

        messages.success(request, "Saved job removed successfully.")
        return redirect('job:view_saved_jobs')

    # If the request is not POST or user not authenticated
    messages.error(request, "Failed to remove saved job.")
    return redirect('job:view_saved_jobs')



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

from django.db.models import Avg
from company.models import Company

def job_details(request,job_id):
    user = request.user
    job = Job.objects.get(id=job_id)
    similar_jobs = Job.objects.annotate(max_matching_percentage=Avg('application__overall_match_percentage')).filter(max_matching_percentage__gte=5.0)
    company = Company.objects.get(job=job)
    all_jobs = Job.objects.all()
    # Initialize the applied job IDs list
    applied_job_ids = []

    # Check if the user is authenticated before querying applications
    if request.user.is_authenticated:
        applied_job_ids = Application.objects.filter(user=request.user).values_list('job_id', flat=True)

    context = {
        'job':job,
        'similar_jobs':similar_jobs,
        'company':company,
        'all_jobs':all_jobs,
        'applied_job_ids':applied_job_ids,
    }
    
    return render(request, "job/job_details.html",context)

#for jobs listing 
from django.http import JsonResponse
from django.core.serializers import serialize
from .models import Job, Company
from django.db.models import Avg

def job_listing_details(request, job_id):
    try:
        job = Job.objects.get(id=job_id)
        similar_jobs = Job.objects.annotate(max_matching_percentage=Avg('application__overall_match_percentage')).filter(max_matching_percentage__gte=5.0)
        company = Company.objects.get(job=job)

        # Serialize the job and similar_jobs queryset to JSON
        job_data = {
            'id': job.id,
            'title': job.title,
            'description': job.description,
            'job_location_type': job.job_location_type,
            'location': str(job.location) if job.location else None, 
            'salary': job.salary,
            'salary_range':job.salary_range,
            'job_type': job.job_type,
            'created_at': job.created_at.strftime('%Y-%m-%d'),  # Format date for better readability
            'company': {
                'name': company.name,
                'location': company.location,
                'logo': company.logo.url if company.logo else None,  # Add company logo if available
            },
        }

        similar_jobs_data = list(similar_jobs.values('id', 'title', 'description'))  # Adjust fields as needed

        response_data = {
            'job': job_data,
            'similar_jobs': similar_jobs_data,
        }

        return JsonResponse(response_data)

    except Job.DoesNotExist:
        return JsonResponse({'error': 'Job not found'}, status=404)
    except Company.DoesNotExist:
        return JsonResponse({'error': 'Company not found'}, status=404)

    
 
def user_applied_jobs(request):
    user = request.user
    # Query all jobs that the user has applied for
    applied_jobs = Job.objects.filter(application__user=user)

    context = {
        'applied_jobs': applied_jobs,
    }

    return render(request, 'job/applied_jobs.html', context)   
def withdraw_application(request, job_id):
    user = request.user
    job = get_object_or_404(Job, id=job_id)
    
    # Find the application for the user and job
    application = Application.objects.filter(user=user, job=job).first()
    
    if application:
        # If the application exists, delete it
        application.delete()
        message = "Your application has been withdrawn."
    else:
        message = "You haven't applied for this job."
    
    # You can redirect to the applied jobs page or some other page after withdrawal
    return redirect('job:applied_jobs')  # or change this to the URL you want to redirect to
    

from .models import SavedJob
from django.views.decorators.http import require_POST

@require_POST  # Ensures that the view only accepts POST requests
def save_job(request, job_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        user = request.user
        job = get_object_or_404(Job, id=job_id)
        
        # Check if the job is already saved
        saved_job, created = SavedJob.objects.get_or_create(user=user, job=job)
        
        if created:
            return JsonResponse({"status": "success", "message": "Job saved successfully.", "action": "saved"})
        else:
            saved_job.delete()  # Optionally, remove the saved job if it was already saved
            return JsonResponse({"status": "success", "message": "Job removed successfully.", "action": "removed"})
    
    # If not an AJAX request
    return JsonResponse({"status": "error", "message": "Invalid request."}, status=400)

def save_job_not_ajax(request, job_id):
    user = request.user
    job = get_object_or_404(Job, id=job_id)

    # Check if the job is already saved
    saved_job, created = SavedJob.objects.get_or_create(user=user, job=job)

    if created:
        messages.success(request, "Job saved successfully.")
    else:
        saved_job.delete()  # Optionally, remove the saved job if it was already saved
        messages.info(request, "Job removed successfully.")

    return redirect('home')  # Redirect to the home page

def remove_saved_job(request, job_id):
    if request.method == "POST" and request.is_ajax():
        user = request.user
        job = get_object_or_404(Job, id=job_id)
        
        saved_job = SavedJob.objects.filter(user=user, job=job).first()
        
        if saved_job:
            saved_job.delete()
            return JsonResponse({"status": "success", "message": "Job removed from saved jobs.", "action": "removed"})
        else:
            return JsonResponse({"status": "error", "message": "This job is not in your saved jobs."})
    return JsonResponse({"status": "error", "message": "Invalid request."})

from django.http import HttpResponse

def saved_jobs_view(request):
    user = request.user

    # Check if the user is authenticated
    if not user.is_authenticated:
        print("User is not authenticated")
        return HttpResponse("You need to be logged in to view saved jobs.")

    # Get the saved jobs for the logged-in user
    saved_jobs = Job.objects.filter(savedjob__user=user)

    # Debug: Print the count of saved jobs
    print(f"Saved jobs count for user {user.username}: {saved_jobs.count()}")

    # Debug: Print each saved job title
    for job in saved_jobs:
        print(f"Saved Job: {job.title}")

    # If no saved jobs, add an extra debug
    if not saved_jobs.exists():
        print("No saved jobs found for the user.")

    context = {
        'saved_jobs': saved_jobs,
    }

    # Debug: Print the context being sent to the template
    print("Context data: ", context)

    return render(request, 'job/saved_jobs.html', context)

logger = logging.getLogger(__name__)

def incomplete_jobs_view(request):
    user = request.user
    print(f"User: {user}")
    
    jobs = Job.objects.all()
    print(f"Total jobs: {jobs.count()}")
    
    incomplete_jobs = []

    for job in jobs:
        print(f"Checking job: {job.title}")
        
        skills = job.requirements.all()
        print(f"Required skills for job '{job.title}': {[skill.name for skill in skills]}")
        print(f"Number of required skills: {skills.count()}")
        
        completed_skills = CompletedSkills.objects.filter(user=user, skill__in=skills)
        print(f"Completed skills for user '{user}': {[cs.skill.name for cs in completed_skills]}")
        print(f"Number of completed skills: {completed_skills.count()}")
        
        for cs in completed_skills:
            print(f"Skill: {cs.skill.name}, Is Completed: {cs.is_completed}")
        
        # Check if completed_skills is not empty and not all required skills are completed
        if completed_skills.exists() and not all(skill in [cs.skill for cs in completed_skills if cs.is_completed] for skill in skills):
            print(f"Job '{job.title}' is incomplete")
            incomplete_jobs.append(job)
        else:
            print(f"Job '{job.title}' is complete")

    print(f"Incomplete jobs: {[job.title for job in incomplete_jobs]}")
    
    return render(request, 'job/incomplete_jobs.html', {'incomplete_jobs': incomplete_jobs})


def success_page(request):
    return render(request, "job/compiler/success.html")

def fail_page(request):
    return render(request, "job/compiler/fail.html")


@login_required  
def shortlist_candidate(request, job_id, candidate_id):  
    job = get_object_or_404(Job, id=job_id)  
    candidate = get_object_or_404(User, id=candidate_id)  
    recruiter = request.user  

    # Determine the company associated with the recruiter  
    # Assuming a one-to-one relationship between User and Company  
    company = get_object_or_404(Company, user=recruiter)  

    # Check if the candidate is already shortlisted for the job  
    if Shortlist.objects.filter(recruiter=recruiter, candidate=candidate, job=job).exists():  
        messages.warning(request, "Candidate is already shortlisted for this job.")  
    else:  
        Shortlist.objects.create(recruiter=recruiter, candidate=candidate, job=job)  
        messages.success(request, "Candidate has been shortlisted successfully.")  
    
    # Redirecting to a URL that takes company_id as a parameter  
    return redirect('job:shortlisted', company_id=company.id)

from resume.models import Resume
from job.utils import calculate_skill_match
@login_required(login_url='login')
def shortlisted_candidates(request, company_id):
    # Check if the current user is the owner of the company
    current_user = request.user
    company = Company.objects.get(id=company_id)
    
    if company.user != current_user:
        return HttpResponse("You are not authorized to view this page.")
    
    jobs = Job.objects.filter(company=company)
    job_applications = {}

    for job in jobs:
        applications = Application.objects.filter(job=job)
        job_applications[job] = applications

    # List to store shortlisted applications
    shortlisted_applications = []

    # Calculate match percentage for each application
    for job, applications in job_applications.items():
        for application in applications:
            user = application.user
            resume = Resume.objects.filter(user=user).first()  # Use filter() to avoid DoesNotExist error
            
            if resume:
                applicant_skills = set(resume.skills.all())
                job_skills = set(job.requirements.all())
                match_percentage, missing_skills = calculate_skill_match(applicant_skills, job_skills)
                application.matching_percentage = match_percentage

                quiz_score = application.quiz_score
                overall_score = match_percentage * 0.7 + (quiz_score / 10) * 0.3
                application.overall_score = overall_score

                application.user.skills_list = list(resume.skills.all())
                application.user.resume = resume
            else:
                application.matching_percentage = 0
                application.overall_score = application.quiz_score / 10 * 0.3  # Only quiz score
                application.user.skills_list = []

            # Add the application to shortlisted list
            shortlisted_applications.append(application)

    context = {
        'company': company,
        'shortlisted_applications': shortlisted_applications,
    }
    
    return render(request, 'company/shortlisted.html', context)

@login_required
def decline_candidate(request, job_id, candidate_id):
    job = get_object_or_404(Job, id=job_id)
    candidate = get_object_or_404(User, id=candidate_id)
    recruiter = request.user

    # Check if the recruiter is associated with the job
    company = get_object_or_404(Company, user=recruiter)
    if job.company != company:
        messages.error(request, "You are not authorized to decline this candidate.")
        return redirect(request.META.get('HTTP_REFERER', 'job:job_applications'))

    # Get the application object
    application = get_object_or_404(Application, job=job, user=candidate)

    # Delete the application object
    application.delete()

    # Send notification to the candidate
    notify_user_declined(candidate, f"Your application for the job '{job.title}' has been declined.", Notification.JOB_APPLICATION)

    # Send email to the candidate
    subject = "Application Declined"
    message = f"""
                Dear {candidate.get_full_name()},

                Thank you for your interest in the {job.title} position at {company.name}. After careful consideration, we regret to inform you that we will not be moving forward with your application at this time.

                We truly appreciate the effort you put into your application and encourage you to apply for future opportunities that align with your qualifications. Thank you again for your time and interest in joining our team.

                Wishing you the very best in your job search.

                Warm regards,  
                {company.name}
                """
    from_email = settings.DEFAULT_FROM_EMAIL
    send_mail(subject, message, from_email, [candidate.email])

    messages.success(request, "Candidate has been declined successfully.")
    
    # Redirect to the previous page (using HTTP_REFERER) or a default fallback if it's not available
    return redirect(request.META.get('HTTP_REFERER', 'job:job_applications'))