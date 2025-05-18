# tasks.py
from celery import shared_task
from .models import Skill, SkillQuestion
import json
import logging
from openai import OpenAI
import os
import dotenv
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from .models import Job

dotenv.load_dotenv()
api_key = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)
logger = logging.getLogger(__name__)

@shared_task  
def generate_questions_task(job_title, entry_level, skill_name, questions_per_skill):  
    questions = []  
    serialized_questions = []  
    success = False  # Track if questions were generated successfully
    
    try:  
        question_data_list = generate_mcqs_for_skill(skill_name, entry_level, job_title)  

        # Retrieve the Job instance
        job_instance = Job.objects.filter(title=job_title).first()
        if not job_instance:
            logger.error(f"Job with title '{job_title}' not found.")
            return {'success': False, 'error': f"Job with title '{job_title}' not found."}

        if question_data_list and isinstance(question_data_list, list):  
            for question_data in question_data_list[:questions_per_skill]:  
                skill = Skill.objects.get(name=skill_name)  
                skill_question = SkillQuestion.objects.create(  
                    question=question_data['question'],  
                    option_a=question_data['options'].get('A', ''),  
                    option_b=question_data['options'].get('B', ''),  
                    option_c=question_data['options'].get('C', ''),  
                    option_d=question_data['options'].get('D', ''),  
                    correct_answer=question_data['correct_answer'],  
                    skill=skill,  
                    entry_level=entry_level,  
                    job=job_instance,  
                    area=question_data['area']  
                )  
                questions.append(skill_question)  
                serialized_questions.append({  
                    'question': skill_question.question,  
                    'option_a': skill_question.option_a,  
                    'option_b': skill_question.option_b,  
                    'option_c': skill_question.option_c,  
                    'option_d': skill_question.option_d,  
                    'correct_answer': skill_question.correct_answer,  
                    'skill': skill_question.skill.name,  
                    'entry_level': skill_question.entry_level,  
                    'area': skill_question.area  
                })  
            success = True  # Set success to True if questions were generated
        else:  
            logger.error("Failed to generate questions for skill: %s", skill_name)  
    
    except Exception as e:  
        logger.error(f"An error occurred while generating questions for skill {skill_name}: {e}")  
    
    # If successful, trigger email notifications
    if success:
        try:
            # Send email to recruiter
            send_recruiter_job_confirmation_email_task.delay(
                email=job_instance.user.email,
                full_name=job_instance.user.get_full_name(),
                job_title=job_instance.title,
                company_name=job_instance.company.name,
                job_id=job_instance.id
            )

            # Send email to users about the new job
            send_new_job_email_task.delay(
                email=job_instance.user.email,
                full_name=job_instance.user.get_full_name(),
                job_title=job_instance.title,
                job_link=f"/jobs/{job_instance.id}/",
                job_description=job_instance.description,
                company_name=job_instance.company.name,
                job_id=job_instance.id
            )
        except Exception as e:
            logger.error(f"Error sending email notifications: {e}")

    return {'success': success, 'questions': serialized_questions}

def generate_mcqs_for_skill(skill_name, entry_level, job_title):
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
    
    
#to send job emails to users



from django.utils.html import strip_tags

logger = logging.getLogger(__name__)

@shared_task(autoretry_for=(), max_retries=0)
def send_new_job_email_task(email, full_name, job_title, job_link, job_description, company_name, job_id):
    subject = f"New Job Posted: {job_title}"
    plain_job_description = strip_tags(job_description)
    message = f"Hello {full_name},\n\nA new job has been posted at {company_name}.\n\nJob Title: {job_title}\nDescription: {plain_job_description}\n\nYou can view the job here: {job_link}\n\nBest regards,\n{company_name}"
    html_message = f"""
    <html>
        <body>
            <p>Hello {full_name},</p>
            <p>A new job has been posted at {company_name}.</p>
            <p><strong>Job Title:</strong> {job_title}</p>
            <p><strong>Description:</strong> {job_description}</p>
            <p>You can view the job <a href="{job_link}">here</a>.</p>
            <p>Best regards,<br>{company_name}</p>
        </body>
    </html>
    """
    from_email = settings.DEFAULT_FROM_EMAIL

    try:
        send_mail(subject, message, from_email, [email], html_message=html_message)
        # Check if all questions were generated successfully before marking the job as complete
        job_instance = Job.objects.get(id=job_id)
        if all(generate_questions_task(job_instance.title, job_instance.level, skill.name, 10)['success'] for skill in job_instance.requirements.all()):
            job_instance.job_creation_is_complete = True
            job_instance.save()
    except Exception as e:
        logger.error(f"An error occurred while sending email to {email}: {e}")

@shared_task(autoretry_for=(), max_retries=0)
def send_recruiter_job_confirmation_email_task(email, full_name, job_title, company_name, job_id):
    subject = f"Job Created Successfully: {job_title}"
    message = f"Hello {full_name},\n\nYour job '{job_title}' has been successfully created and is now available on the platform at {company_name}.\n\nBest regards,\n{company_name}"
    html_message = f"""
    <html>
        <body>
            <p>Hello {full_name},</p>
            <p>Your job '<strong>{job_title}</strong>' has been successfully created and is now available on the platform at {company_name}.</p>
            <p>Best regards,<br>UmEmployed Team</p>
        </body>
    </html>
    """
    from_email = settings.DEFAULT_FROM_EMAIL

    try:
        send_mail(subject, message, from_email, [email], html_message=html_message)
        # Check if all questions were generated successfully before marking the job as complete
        job_instance = Job.objects.get(id=job_id)
        if all(generate_questions_task(job_instance.title, job_instance.level, skill.name, 10)['success'] for skill in job_instance.requirements.all()):
            job_instance.job_creation_is_complete = True
            job_instance.save()
    except Exception as e:
        logger.error(f"An error occurred while sending email to {email}: {e}")