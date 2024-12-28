from django.shortcuts import render, redirect, get_object_or_404
import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .tasks import generate_questions_task
from .models import Skill
import os
import dotenv

dotenv.load_dotenv()
logger = logging.getLogger(__name__)

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
            questions_per_skill = 5

            for skill_name in selected_skill_names:
                generate_questions_task.delay(job_title, entry_level, skill_name, questions_per_skill)

            return redirect('index')  # Redirect to the next page immediately

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return JsonResponse({"error": "An error occurred"}, status=500)

    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)