from django.shortcuts import render, redirect
from .models import GeneralKnowledgeQuestion, GeneralKnowledgeAnswer, QuizResponse
from resume.models import Resume

def general_knowledge_quiz(request):
    if request.method == 'POST':
        # Process the user's answers and save them to the QuizResponse model
        questions = GeneralKnowledgeQuestion.objects.all()[:5]  # Assuming you want to display 5 questions
        resume = Resume.objects.get(user=request.user)
        for question in questions:
            answer_id = request.POST.get(f"question{question.id}")
            if answer_id:
                answer = GeneralKnowledgeAnswer.objects.get(id=answer_id)
                QuizResponse.objects.create(resume=resume, answer=answer)
        
        # After processing the answers, you can redirect to a results page or perform other actions
        return redirect('quiz_results')  # Replace 'results_page' with the actual URL name for the results page
    else:
        # Retrieve random questions from the database
        questions = GeneralKnowledgeQuestion.objects.all()[:5]  # Assuming you want to display 5 questions
        context = {
            'questions': questions
        }
        return render(request, 'onboarding/general_knowledge_quiz.html', context)



from .models import Resume, QuizResponse

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

    # Pass the quiz responses, score, and total number of questions to the template
    context = {
        'quiz_responses': quiz_responses,
        'score': score,
        'total_questions': total_questions
    }
    return render(request, 'onboarding/quiz_results.html', context)
