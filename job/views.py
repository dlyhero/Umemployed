from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from .models import Job, Application
from .forms import CreateJobForm , UpdateJobForm,SkillForm
from resume.views import get_matching_jobs
from django.contrib.auth.decorators import login_required
from onboarding.views import general_knowledge_quiz
from resume.models import Skill,SkillCategory
from job.models import Job
import json
from .jdoodle_api import execute_code
from django.http import JsonResponse, HttpResponseNotAllowed
from django.shortcuts import render


# create a job
# views.py

from django.contrib import messages
from django.shortcuts import redirect, render

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Job, MCQ
from .forms import CreateJobForm

@login_required(login_url='/login')
def create_job(request):
    if request.user.is_recruiter and request.user.has_company:
        if request.method == 'POST':
            form = CreateJobForm(request.POST)
            if form.is_valid():
                job = form.save(commit=False)
                job.user = request.user
                job.company = request.user.company
                job.save()

                # Retrieve questions from the MCQ model based on the job title
                questions = MCQ.objects.filter(job_title=job.title)

                # Store the questions in the session
                request.session['job_questions'] = list(questions.values_list('question', flat=True))

                # Store the selected category in the session
                request.session['selected_category'] = form.cleaned_data['category'].id
                request.session['selected_job_id'] = job.id

                messages.info(request, "Update Recorded")
                return redirect('job:select_skills')
            else:
                messages.warning(request, 'Something went wrong')
                return redirect('create_job')
        else:
            form = CreateJobForm()
            context = {'form': form}
            return render(request, 'job/create_job.html', context)
    else:
        messages.warning(request, 'Permission Denied!')
        return redirect('dashboard')


def select_skills(request):
    if request.user.is_recruiter and request.user.has_company:
        selected_category_id = request.session.get('selected_category')
        selected_job_id = request.session.get('selected_job_id')
        if selected_category_id and selected_job_id:
            selected_category = SkillCategory.objects.get(id=selected_category_id)
            job_instance = Job.objects.get(id=selected_job_id)

            if request.method == 'POST':
                form = SkillForm(request.POST, category=selected_category, instance=job_instance)
                if form.is_valid():
                    form.save()
                    messages.info(request, "Skills added successfully")
                    return redirect('dashboard')
            else:
                form = SkillForm(category=selected_category)

            return render(request, 'job/skill.html', {'form': form})
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
from .models import Job, MCQ, ApplicantAnswer
from .forms import ApplicantAnswerForm

from django.db.models import F

@login_required(login_url='/login')
def answer_job_questions(request, job_id):
    job = get_object_or_404(Job, id=job_id)

    if request.method == 'POST':
        answers = request.POST
        if answers:
            total_score = 0  # Initialize total score
            for mcq in MCQ.objects.filter(job_title=job.category):
                answer = answers.get(f'question{mcq.id}')
                if answer:
                    applicant_answer = ApplicantAnswer.objects.create(
                        applicant=request.user,
                        question=mcq,
                        answer=answer,
                        job=job
                    )
                    applicant_answer.calculate_score()  # Calculate score for each answer
                    total_score += applicant_answer.score  # Update total score
            
            # Create a new instance of the Application model
            application = Application(user=request.user, job=job)
            application.has_completed_quiz = True  # Set has_completed_quiz to True
            application.save()  # Save the application
            
            messages.success(request, f"Your answers have been recorded. Total score: {total_score}")
            return redirect('job:job_application_success')
        else:
            messages.error(request, "Please answer all questions.")
            return redirect('job:answer_job_questions', job_id=job_id)
    else:
        mcqs = MCQ.objects.filter(job_title=job.title)
        context = {
            'job': job,
            'mcqs': mcqs,
        }
        return render(request, 'job/job_quiz.html', context)
def job_application_success(request):
    return render(request, 'job/application_success.html')





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