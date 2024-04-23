from django.http import JsonResponse
from .models import MCQ
from resume.models import Skill, SkillCategory
import json
import openai
from openai import OpenAI

import os
import dotenv
dotenv.load_dotenv()
from .models import MCQ, SkillCategory



api_key = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

def save_skills_to_database(job_title, skills):
    """
    Save skills to the database.

    Args:
        job_title (str): The title of the job.
        skills (list): List of skills associated with the job.
    """
    try:
        # Retrieve or create the SkillCategory object based on the job_title
        category, created = SkillCategory.objects.get_or_create(name=job_title)

        # Create Skill objects and associate them with the SkillCategory
        for skill_name in skills:
            skill, created = Skill.objects.get_or_create(name=skill_name)
            skill.categories.add(category)  # Associate the skill with the category

    except Exception as e:
        print(f"An error occurred while saving skills to the database for {job_title}: {e}")


def save_mcqs_to_database(skill_category_name, mcqs_data):
    """
    Save MCQs to the database.

    Args:
        skill_category_name (str): The name of the skill category.
        mcqs_data (dict): Data containing MCQs information.
    """
    try:
        # Retrieve or create the SkillCategory object based on the skill_category_name
        skill_category, created = SkillCategory.objects.get_or_create(name=skill_category_name)

        # Create MCQ objects and associate them with the SkillCategory
        mcq = MCQ.objects.create(
            question=mcqs_data['question'],
            option_a=mcqs_data['options']['A'],
            option_b=mcqs_data['options']['B'],
            option_c=mcqs_data['options']['C'],
            option_d=mcqs_data['options']['D'],
            correct_answer=mcqs_data['correct_answer'],
            job_title=skill_category  # Assigning the SkillCategory instance
        )

    except Exception as e:
        print(f"An error occurred while saving MCQs to the database for {skill_category_name}: {e}")


def generate_mcqs(job_title):
    """
    Generate multiple-choice questions related to a job title.

    Args:
        job_title (str): The title of the job.

    Returns:
        list: List of generated MCQs.
    """
    conversation = [
        {
            "role": "user", 
            "content": f"Generate 1 technical multiple-choice question and answers related to the job title: {job_title}. Each question should be followed by four answer choices (A, B, C, D) and a correct answer indicated. Ensure that the response is provided in JSON format, where the MCQ is represented as an object with the following structure: \n\n{{\n  \"question\": \"\",\n  \"options\": {{\n    \"A\": \"\",\n    \"B\": \"\",\n    \"C\": \"\",\n    \"D\": \"\"\n  }},\n  \"correct_answer\": \"\"\n}}"
        }
    ]

    try:
        # Make a request to the ChatGPT API using the initialized client
        response = client.chat.completions.create(
            model="gpt-4",
            messages=conversation
        )

        # Extract the generated MCQs and answers from the chat-based response
        mcqs_and_answers = response.choices[0].message.content

        try:
            # Attempt to parse the response as JSON
            mcqs_and_answers_list = json.loads(mcqs_and_answers)
            return mcqs_and_answers_list
        except json.JSONDecodeError as e:
            # Handle parsing error gracefully
            print("Failed to parse MCQs response:", e)
            return None

    except Exception as e:
        # Handle other errors
        print("An error occurred while generating MCQs:", e)
        return None


def get_skills_from_chatgpt(job_title):
    """
    Generate skills related to a job title.

    Args:
        job_title (str): The title of the job.

    Returns:
        dict: Dictionary containing the job title and associated skills.
    """
    conversation = [
        {
            "role": "user",
            "content": f"What are the key skills, tools (technologies) required for {job_title}? Provide a response that is straight to the point and the skills should be just one or two words, also avoid numbering the skills/tools. These skills/tools should be individual items in a list of skills for that particular job_title. Let the various technologies and sub-skills be listed as well and any related skill/tool to that job. In place where there are subcategories to a skill, just list the subcategories too as skills, same format."
        }
    ]

    try:
        # Make a request to the ChatGPT API using the initialized client
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=conversation
        )

        content = response.choices[0].message.content
        skills = content.strip().split("\n")

        return {"job_title": job_title, "skills": skills}
    except Exception as e:
        print(f"An error occurred while generating skills for {job_title}: {e}")
        return None



def execute_input(request):
    """
    Execute input and generate skills and MCQs.

    Args:
        request: The HTTP request object.

    Returns:
        JsonResponse: JSON response containing generated skills and MCQs.
    """
    if request.method == 'GET':
        input_str = request.GET.get('input_str')

        existing_skill_category = SkillCategory.objects.filter(name=input_str).first()
        existing_mcqs = MCQ.objects.filter(job_title=existing_skill_category).first()

        if existing_skill_category and existing_mcqs:
            # Fetch skills associated with the existing skill category
            existing_skills = Skill.objects.filter(categories=existing_skill_category)
            return JsonResponse({
                "message": "Skills and MCQs already exist in the database",
                "skills": [skill.name for skill in existing_skills],
                "mcqs": {
                    "question": existing_mcqs.question,
                    "option_A": existing_mcqs.option_a,
                    "option_B": existing_mcqs.option_b,
                    "option_C": existing_mcqs.option_c,
                    "option_D": existing_mcqs.option_d,
                    "correct_answer": existing_mcqs.correct_answer
                }
            })

        mcqs = []
        for _ in range(5):
            mcq = generate_mcqs(input_str)
            if mcq is not None:
                mcqs.append(mcq)

        skills = get_skills_from_chatgpt(input_str)

        if mcqs:
            for mcq in mcqs:
                save_mcqs_to_database(input_str, mcq)

        if skills is not None:
            save_skills_to_database(input_str, skills["skills"])

        return JsonResponse({
            "message": "Skills and MCQs generated and stored successfully",
            "skills": skills["skills"] if skills else [],
            "mcqs": mcqs if mcqs else {}
        })
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)
