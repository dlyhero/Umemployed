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
from resume.models import SkillCategory,Skill
api_key = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)
logger = logging.getLogger(__name__)

import json
import logging

# Get an instance of a logger
logger = logging.getLogger(__name__)


api_key = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

def save_skills_to_database(job_title, skills):
    """
    Save skills extracted from job descriptions to the database.

    Args:
        job_title (str): The title of the job.
        skills (list): List of skills extracted from the job description.
    """
    try:
        # Retrieve or create the SkillCategory object based on the job_title
        category, created = SkillCategory.objects.get_or_create(name=job_title)

        # Create Skill objects and associate them with the SkillCategory
        for skill_name in skills:
            skill, created = Skill.objects.get_or_create(name=skill_name)
            skill.categories.add(category)  # Associate the skill with the category
            skill.is_extracted = True  # Set the flag indicating that this skill was extracted from a job description
            skill.save()

    except Exception as e:
        logger.error("An error occurred while saving skills to the database for %s: %s", job_title, e)

def extract_technical_skills(job_title, job_description):
    """
    Extract technical skills from a job description using GPT-4.

    Args:
        job_title (str): The title of the job.
        job_description (str): The description of the job.

    Returns:
        list: List of technical skills extracted from the job description.
    """
    conversation = [
        {
            "role": "user", 
            "content": f"Given the following job description (JD): {job_description}, identify and list up all the technical skills that can be practically tested during a technical interview. Focus on extracting skills related to hands-on technical knowledge, coding abilities, use of specific software tools, problem-solving skills, and any other competencies that can be demonstrated through practical tests, coding challenges, or problem-solving exercises. Exclude skills that cannot be directly tested in an interview setting, such as soft skills or theoretical knowledge not applicable to practical tasks. Format your output in JSON, organizing the skills under a key named 'Technical Skills'. Each skill should be listed as an element in an array of strings. Ensure that each skill does not comprise more than two words."
        }
    ]

    try:
        # Call GPT-4 to generate technical skills based on job description
        response = client.chat.completions.create(
            model="gpt-4",
            messages=conversation,
            timeout=120  # Extended timeout to 120 seconds
        )

        # Parse the response
        response_content = response.choices[0].message.content
        response_dict = json.loads(response_content)
        
        # Extract the technical skills
        technical_skills = response_dict.get("Technical Skills", [])

        # Save the skills to the database
        save_skills_to_database(job_title, technical_skills)
        print('Skills saved to database:', technical_skills)

        return technical_skills

    except (json.JSONDecodeError, Exception) as e:
        logger.error("An error occurred while extracting technical skills: %s", e)
        return []



def extract_technical_skills_endpoint(request):
    """
    Extract technical skills from a job description using a POST request.

    Args:
        request: The HTTP request object.

    Returns:
        JsonResponse: JSON response containing the extracted technical skills.
    """
    # Get the job description from the query parameters
    job_description = request.GET.get('job_description', '')
    job_title = request.GET.get('job_title', '')
    
    # Validate input
    if not job_description or not job_title:
        return JsonResponse({"error": "Job title and job description are required."}, status=400)

    # Call function to extract technical skills
    result = extract_technical_skills(job_title, job_description)

    # If no results were found, return an error response
    if result is None:
        return JsonResponse({"error": "An error occurred while extracting technical skills."}, status=500)

    # Otherwise, return the results as JSON response
    else:
        return JsonResponse(result)

    