from django.shortcuts import render, redirect
from .models import GeneralKnowledgeQuestion, GeneralKnowledgeAnswer, QuizResponse
from resume.models import Resume
from job.models import Application

def general_knowledge_quiz(request):
    if request.method == 'POST':
        if request.session.get('quiz_submitted'):
            # If the quiz has already been submitted, redirect to the results page
            return redirect('quiz_results')
        
        # Process the user's answers and save them to the QuizResponse model
        questions = GeneralKnowledgeQuestion.objects.all()[:10]  # Assuming you want to display 10 questions
        resume = Resume.objects.get(user=request.user)
        applications = Application.objects.filter(user=request.user)
        score = 0  # Initialize the score
        for question in questions:
            answer_id = request.POST.get(f"question{question.id}")
            if answer_id:
                answer = GeneralKnowledgeAnswer.objects.get(id=answer_id)
                QuizResponse.objects.create(resume=resume, answer=answer)
                if answer.is_correct:
                    score += 1
        
        # Update the quiz score in each application model
        for application in applications:
            application.quiz_score = score
            application.save()
        
        # Mark the quiz as submitted in the session
        request.session['quiz_submitted'] = True
        
        # After processing the answers, you can redirect to a results page or perform other actions
        return redirect('quiz_results')  # Replace 'quiz_results' with the actual URL name for the results page
    else:
        if request.session.get('quiz_submitted'):
            # If the quiz has already been submitted, redirect to the results page
            return redirect('quiz_results')
        
        # Retrieve random questions from the database
        questions = GeneralKnowledgeQuestion.objects.all()[:10]  # Assuming you want to display 10 questions
        context = {
            'questions': questions
        }
        return render(request, 'onboarding/general_knowledge_quiz.html', context)
def quiz_results(request):
    resume = Resume.objects.get(user=request.user)
    applications = Application.objects.filter(user=request.user)
    quiz_responses = QuizResponse.objects.filter(resume=resume)

    # Get all questions and options
    questions = GeneralKnowledgeQuestion.objects.all()

    # Create a dictionary to store the correct options of each question
    correct_options = {}
    for question in questions:
        correct_options[question.id] = GeneralKnowledgeAnswer.objects.filter(question=question, is_correct=True).first()

    # Iterate over the applications and calculate the score for each one
    for application in applications:
        score = 0
        for quiz_response in quiz_responses:
            if quiz_response.answer.question.id in correct_options:
                correct_option = correct_options[quiz_response.answer.question.id]
                if quiz_response.answer == correct_option:
                    score += 1
        application.quiz_score = score
        application.save()

    # Calculate the additional context variables
    total_questions = len(questions)

    # Add the additional context
    context = {
        'quiz_responses': quiz_responses,
        'score': score,
        'total_questions': total_questions,
        'questions': questions,
        'correct_options': correct_options,
    }

    # Pass the updated context to the template
    return render(request, 'onboarding/quiz_results.html', context)