from django.shortcuts import render, redirect, get_object_or_404
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
    """
    Generates and stores multiple-choice questions for selected skills based on job title and entry level.

    Args:
        request: HTTP request object.

    Returns:
        If successful, redirects to a specified URL; otherwise, returns a JSON response with an error message.

    Raises:
        HTTPError: If the request method is not allowed.
    """
    if request.method == 'GET':
        job_title = request.GET.get('job_title')
        entry_level = request.GET.get('entry_level')
        selected_skills = request.GET.get('selected_skills')
        selected_skill_names = selected_skills.split(',') if selected_skills else []

        try:
            questions_per_skill = 10
            all_questions = []

            for skill_name in selected_skill_names:
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
                        'entry_level': question.entry_level,
                        'area': question.area  # Include the area in the serialized data
                    }
                    serialized_questions.append(serialized_question)

                return redirect('/')
            else:
                return JsonResponse({"error": "Failed to generate questions"}, status=500)

        except Exception as e:
            logging.error(f"An error occurred: {e}")
            return JsonResponse({"error": "An error occurred"}, status=500)

    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)

def generate_questions_for_skills(job_title, entry_level, skill_name, questions_per_skill):
    """
    Generates multiple-choice questions for a specified skill.

    Args:
        job_title (str): The job title.
        entry_level (str): The entry level of the job.
        skill_name (str): The name of the skill.
        questions_per_skill (int): The number of questions to generate for the skill.

    Returns:
        A list of SkillQuestion objects containing the generated questions.

    Raises:
        None
    """
    questions = []
    
    try:
        question_data_list = generate_mcqs_for_skill(skill_name, entry_level, job_title)
        
        if question_data_list and isinstance(question_data_list, list):
            for question_data in question_data_list[:questions_per_skill]:
                skill_question = SkillQuestion.objects.create(
                    question=question_data['question'],
                    option_a=question_data['options'].get('A', ''),
                    option_b=question_data['options'].get('B', ''),
                    option_c=question_data['options'].get('C', ''),
                    option_d=question_data['options'].get('D', ''),
                    correct_answer=question_data['correct_answer'],
                    skill=Skill.objects.get(name=skill_name),
                    entry_level=entry_level,
                    area=question_data['area']  # Save the area of expertise
                )
                questions.append(skill_question)
        else:
            print("Failed to generate question for skill:", skill_name)
    
    except Exception as e:
        print(f"An error occurred while generating questions for skill {skill_name}: {e}")
    
    return questions

def generate_mcqs_for_skill(skill_name, entry_level, job_title):
    """
    Generates a set of 10 technical multiple-choice questions and answers related to a specified skill,
    tailored for a specific job position and level.

    Args:
        skill_name (str): The name of the skill.
        entry_level (str): The entry level of the job position.
        job_title (str): The job title.

    Returns:
        A list of dictionaries containing the generated questions, answer options, correct answers, and areas of expertise.

    Raises:
        None
    """
    conversation = [
        {
            "role": "user", 
            "content": f"Generate a set of 10 technical multiple-choice questions and answers related to the skill of {skill_name}, specifically tailored for a {entry_level} {job_title} position. Ensure that the questions cover the five key interview areas most relevant for this role. Each question should be followed by four answer choices (A, B, C, D) and include a correct answer.\n\nThe response should be formatted in JSON, with each multiple-choice question represented as an object structured as follows:\n{{\n  \"question\": \"\",\n  \"options\": {{\n    \"A\": \"\",\n    \"B\": \"\",\n    \"C\": \"\",\n    \"D\": \"\"\n  }},\n  \"correct_answer\": \"\",\n  \"area\": \"\"\n}}\nPlease ensure that the area of expertise related to each question is also specified within the JSON object."
        }
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=conversation,
            timeout=120
        )

        mcqs_and_answers = response.choices[0].message.content
        mcqs_and_answers_list = json.loads(mcqs_and_answers)
        
        if isinstance(mcqs_and_answers_list, list):
            return mcqs_and_answers_list
        else:
            logger.error("Unexpected format for MCQs data: %s", mcqs_and_answers_list)
            return None

    except (json.JSONDecodeError, Exception) as e:
        logger.error("An error occurred while generating MCQs for skill %s: %s", skill_name, e)
        return None