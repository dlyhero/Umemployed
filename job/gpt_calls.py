from django.http import JsonResponse
from resume.models import Skill, SkillCategory
import json
import openai
from openai import OpenAI
import os
import dotenv

dotenv.load_dotenv()

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
    pass  # No logic implemented

def generate_mcqs(job_title):
    """
    Generate multiple-choice questions related to a job title.

    Args:
        job_title (str): The title of the job.

    Returns:
        list: List of generated MCQs.
    """
    pass  # No logic implemented

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
            messages=conversation,
            timeout=120
        )

        content = response.choices[0].message.content
        skills = content.strip().split("\n")

        return {"job_title": job_title, "skills": skills}
    except Exception as e:
        print(f"An error occurred while generating skills for {job_title}: {e}")
        return None

def execute_input(request):
    """
    Execute input and generate skills.

    Args:
        request: The HTTP request object.

    Returns:
        JsonResponse: JSON response containing generated skills.
    """
    if request.method == 'GET':
        input_str = request.GET.get('input_str')

        existing_skill_category = SkillCategory.objects.filter(name=input_str).first()

        if existing_skill_category:
            # Fetch skills associated with the existing skill category
            existing_skills = Skill.objects.filter(categories=existing_skill_category)
            return JsonResponse({
                "message": "Skills already exist in the database",
                "skills": [skill.name for skill in existing_skills]
            })

        skills = get_skills_from_chatgpt(input_str)

        if skills is not None:
            save_skills_to_database(input_str, skills["skills"])

        return JsonResponse({
            "message": "Skills generated and stored successfully",
            "skills": skills["skills"] if skills else []
        })
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)