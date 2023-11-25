from django.shortcuts import render, redirect
from .models import GeneralKnowledgeQuestion, GeneralKnowledgeAnswer, QuizResponse
from resume.models import Resume

def general_knowledge_quiz(request):
    if request.method == 'POST':
        if request.session.get('quiz_submitted'):
            # If the quiz has already been submitted, redirect to the results page
            return redirect('quiz_results')
        
        # Process the user's answers and save them to the QuizResponse model
        questions = GeneralKnowledgeQuestion.objects.all()[:10]  # Assuming you want to display 10 questions
        resume = Resume.objects.get(user=request.user)
        for question in questions:
            answer_id = request.POST.get(f"question{question.id}")
            if answer_id:
                answer = GeneralKnowledgeAnswer.objects.get(id=answer_id)
                QuizResponse.objects.create(resume=resume, answer=answer)
        
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
    quiz_responses = QuizResponse.objects.filter(resume=resume)

    # Calculate the score and total number of questions
    score = 0
    total_questions = 0
    for response in quiz_responses:
        if response.answer.is_correct:
            score += 1
        total_questions += 1

    # Get all questions and options
    questions = GeneralKnowledgeQuestion.objects.all()

    # Create a dictionary to store the correct options of each question
    correct_options = {}
    for question in questions:
        correct_options[question.id] = GeneralKnowledgeAnswer.objects.filter(question=question, is_correct=True).first()

    # Pass the quiz responses, score, total number of questions, questions, and correct options to the template
    context = {
        'quiz_responses': quiz_responses,
        'score': score,
        'total_questions': total_questions,
        'questions': questions,
        'correct_options': correct_options,
    }
    return render(request, 'onboarding/quiz_results.html', context)