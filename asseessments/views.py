from django.shortcuts import render,redirect,get_object_or_404
from .models import Assessment, Session, Result, Question, Option
from .forms import AssessmentForm, QuestionForm, OptionForm
from django.utils import timezone
from django.urls import reverse 


# Create your views here.
def assessments(request):
    user = request.user  # Assuming you have authentication in place
    sessions = Session.objects.filter(user=user).order_by('-id')[:3]
    assessments = Assessment.objects.filter(session__in=sessions).distinct()
    context = {'assessments': assessments, 'sessions': sessions}
    return render(request, 'assessments/assessment.html', context)

def assessment_detail(request):
    return render(request, 'assessments/assessment_detail.html')



def assessment_list(request):
    assessments = Assessment.objects.all()
    return render(request, 'assessment/assessment_list.html', {'assessments': assessments})

def assessment_detail(request, assessment_id):
    assessments = Assessment.objects.all()
    assessment = get_object_or_404(Assessment, id=assessment_id)
    context = {'assessment': assessment, 'assessments':assessments}
    return render(request, 'assessments/assessment_detail.html',context)



# View to create a new assessment
def create_assessment(request):
    if request.method == 'POST':
        form = AssessmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('assessment_list')
    else:
        form = AssessmentForm()
    return render(request, 'assessments/create_assessment.html', {'form': form})

# View to update an existing assessment
def update_assessment(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id)
    if request.method == 'POST':
        form = AssessmentForm(request.POST, instance=assessment)
        if form.is_valid():
            form.save()
            return redirect('assessment_list')
    else:
        form = AssessmentForm(instance=assessment)
    return render(request, 'assessments/update_assessment.html', {'form': form})

# View to delete an assessment
def delete_assessment(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id)
    if request.method == 'POST':
        assessment.delete()
        return redirect('assessment_list')
    return render(request, 'assessments/delete_assessment.html', {'assessment': assessment})

# Views for Question and Option can be implemented similarly

# View to list all assessments
def assessment_list(request):
    assessments = Assessment.objects.all()
    return render(request, 'assessments/assessment_list.html', {'assessments': assessments})


# View to display available assessments for the user
def available_assessments(request):
    assessments = Assessment.objects.all()
    return render(request, 'assessments/user/available_assessments.html', {'assessments': assessments})

def session_details(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    return render(request, 'assessments/user/session_details.html', {'session': session})
# View to start a new session for an assessment
def start_session(request, assessment_id):
    assessment = get_object_or_404(Assessment, id=assessment_id)
    user = request.user  # Assuming you have authentication in place
    session = Session.objects.create(user=user, assessment=assessment)
    
    # Render the start session template
    render(request, 'assessments/user/start_session.html', {'session': session})
    
    # Determine the URL to redirect the user to
    redirect_url = reverse('session_details', args=[session.id])
    
    return redirect(redirect_url)

# View to submit a session (end the assessment)
def submit_session(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    if request.method == 'POST':
        # Process the submitted session and store the results
        # You can access the selected options from the request.POST data
        # and create Result objects accordingly
        # ...
        session.end_time = timezone.now()
        session.save()
        return redirect('session_results', session_id=session_id)
    return render(request, 'assessments/user/submit_session.html', {'session': session})

# View to display the results of a session
def session_results(request, session_id):
    session = get_object_or_404(Session, id=session_id)
    results = Result.objects.filter(session=session)
    return render(request, 'assessments/user/session_results.html', {'session': session, 'results': results})