from django.shortcuts import render,redirect,get_object_or_404
import json
import logging
from openai import OpenAI
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Skill, SkillQuestion
import os
import dotenv
dotenv.load_dotenv()


api_key = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)
logger = logging.getLogger(__name__)

@csrf_exempt
def generate_questions_view(request):
    if request.method == 'GET':
        job_title = request.GET.get('job_title')
        entry_level = request.GET.get('entry_level')
        selected_skills = request.GET.get('selected_skills')
        selected_skill_names = selected_skills.split(',') if selected_skills else []

        print("Selected job title:", job_title)
        print("Selected entry level:", entry_level)
        print("Selected skills:", selected_skill_names)

        try:
            questions_per_skill = 3  # Number of questions to generate for each skill
            all_questions = []  # List to store all generated questions

            for skill_name in selected_skill_names:
                # Generate questions for each selected skill
                questions = generate_questions_for_skills(job_title, entry_level, skill_name, questions_per_skill)
                all_questions.extend(questions)

            if all_questions:
                serialized_questions = []
                for question in all_questions:
                    serialized_question = {
                        'question': question.question,
                        'option_a': question.option_a,
                        'option_b': question.option_b,
                        'option_c': question.option_c,
                        'option_d': question.option_d,
                        'correct_answer': question.correct_answer,
                        'skill': question.skill.name,
                        'entry_level': question.entry_level
                    }
                    serialized_questions.append(serialized_question)

                print("Serialized questions:", serialized_questions)
                # return JsonResponse({"message": "Questions generated successfully", "questions": serialized_questions})
                return redirect('/')
            else:
                return JsonResponse({"error": "Failed to generate questions"}, status=500)

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            print("An error occurred:", e)
            return JsonResponse({"error": "An error occurred"}, status=500)

    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)

def generate_questions_for_skills(job_title, entry_level, skill_name, questions_per_skill):
    print("Generating questions for job title:", job_title)
    print("Generating questions for skill:", skill_name)
    
    questions = []
    
    try:
        # Generate questions for the specified skill
        for _ in range(questions_per_skill):
            question_data = generate_mcqs_for_skill(skill_name)
            
            if question_data:
                # Create a SkillQuestion object and associate it with the Skill
                skill_question = SkillQuestion.objects.create(
                    question=question_data['question'],
                    option_a=question_data['options'].get('A', ''),
                    option_b=question_data['options'].get('B', ''),
                    option_c=question_data['options'].get('C', ''),
                    option_d=question_data['options'].get('D', ''),
                    correct_answer=question_data['correct_answer'],
                    skill=Skill.objects.get(name=skill_name),
                    entry_level=entry_level
                )
                questions.append(skill_question)
            else:
                print("Failed to generate question for skill:", skill_name)
    
    except Exception as e:
        print(f"An error occurred while generating questions for skill {skill_name}: {e}")
    
    return questions
def generate_mcqs_for_skill(skill_name):
    conversation = [
        {
            "role": "user", 
            "content": f"Generate 1 technical multiple-choice question and answers related to the skill: {skill_name}. Each question should be followed by four answer choices (A, B, C, D) and a correct answer indicated. Ensure that the response is provided in JSON format, where the MCQ is represented as an object with the following structure: \n\n{{\n  \"question\": \"\",\n  \"options\": {{\n    \"A\": \"\",\n    \"B\": \"\",\n    \"C\": \"\",\n    \"D\": \"\"\n  }},\n  \"correct_answer\": \"\"\n}}"
        }
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=conversation
        )

        mcqs_and_answers = response.choices[0].message.content
        mcqs_and_answers_list = json.loads(mcqs_and_answers)
        
        if isinstance(mcqs_and_answers_list, dict):
            return mcqs_and_answers_list
        else:
            logger.error("Unexpected format for MCQs data: %s", mcqs_and_answers_list)
            return None

    except (json.JSONDecodeError, Exception) as e:
        logger.error("An error occurred while generating MCQs for skill %s: %s", skill_name, e)
        return None
