# tasks.py
import json
import logging
import os

import dotenv
from celery import shared_task
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from openai import OpenAI

from .models import Job, Skill, SkillQuestion

dotenv.load_dotenv()
api_key = os.environ.get("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)
logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 3, 'countdown': 60})
def generate_questions_task(self, job_title, entry_level, skill_name, questions_per_skill):
    """
    Generate questions for a specific skill in a job.
    
    Args:
        job_title: Title of the job
        entry_level: Experience level for the skill
        skill_name: Name of the skill to generate questions for
        questions_per_skill: Number of questions to generate
    
    Returns:
        dict: Success status and generated questions
    """
    questions = []
    serialized_questions = []
    success = False

    try:
        logger.info(f"Starting question generation for skill '{skill_name}' in job '{job_title}'")
        
        # Check if questions already exist for this skill-job combination
        job_instance = Job.objects.filter(title=job_title).first()
        if not job_instance:
            logger.error(f"Job with title '{job_title}' not found.")
            return {"success": False, "error": f"Job with title '{job_title}' not found."}

        skill_obj = Skill.objects.get(name=skill_name)
        existing_questions = SkillQuestion.objects.filter(
            job=job_instance, 
            skill=skill_obj
        ).count()
        
        if existing_questions >= questions_per_skill:
            logger.info(f"Questions already exist for skill '{skill_name}' in job '{job_title}'")
            return {"success": True, "questions": [], "message": "Questions already exist"}

        question_data_list = generate_mcqs_for_skill(skill_name, entry_level, job_title)

        if question_data_list and isinstance(question_data_list, list):
            # Use bulk_create for better performance
            skill_questions_to_create = []
            skill = Skill.objects.get(name=skill_name)
            
            for question_data in question_data_list[:questions_per_skill]:
                skill_question = SkillQuestion(
                    question=question_data["question"],
                    option_a=question_data["options"].get("A", ""),
                    option_b=question_data["options"].get("B", ""),
                    option_c=question_data["options"].get("C", ""),
                    option_d=question_data["options"].get("D", ""),
                    correct_answer=question_data["correct_answer"],
                    skill=skill,
                    entry_level=entry_level,
                    job=job_instance,
                    area=question_data["area"],
                )
                skill_questions_to_create.append(skill_question)
                
                # Prepare serialized data for response
                serialized_questions.append(
                    {
                        "question": question_data["question"],
                        "option_a": question_data["options"].get("A", ""),
                        "option_b": question_data["options"].get("B", ""),
                        "option_c": question_data["options"].get("C", ""),
                        "option_d": question_data["options"].get("D", ""),
                        "correct_answer": question_data["correct_answer"],
                        "skill": skill.name,
                        "entry_level": entry_level,
                        "area": question_data["area"],
                    }
                )
            
            # Bulk create all questions at once
            created_questions = SkillQuestion.objects.bulk_create(
                skill_questions_to_create, 
                ignore_conflicts=True
            )
            questions.extend(created_questions)
            success = True
            logger.info(f"Successfully bulk created {len(created_questions)} questions for skill '{skill_name}'")
        else:
            logger.error("Failed to generate questions for skill: %s", skill_name)

    except Exception as e:
        logger.error(f"An error occurred while generating questions for skill {skill_name}: {e}")

    # If successful, check if all skills have questions and mark job as complete
    if success:
        try:
            # Use atomic transaction to prevent race conditions
            from django.db import transaction
            
            with transaction.atomic():
                # Get fresh job instance within transaction
                job_instance = Job.objects.select_for_update().filter(title=job_title).first()
                if not job_instance:
                    logger.error(f"Job with title '{job_title}' not found")
                    return {"success": success, "questions": serialized_questions}
                
                # Skip if already marked complete (another task beat us to it)
                if job_instance.job_creation_is_complete:
                    logger.info(f"Job '{job_title}' already marked as complete")
                    return {"success": success, "questions": serialized_questions}
                
                # Update progress tracking
                progress = job_instance.questions_generation_progress or {}
                skill_obj = Skill.objects.get(name=skill_name)
                progress[str(skill_obj.id)] = True
                job_instance.questions_generation_progress = progress
                
                # Check if all skills now have questions
                all_skills = job_instance.requirements.all()
                skills_with_questions = SkillQuestion.objects.filter(
                    job=job_instance
                ).values_list('skill_id', flat=True).distinct()
                
                required_skill_ids = set(all_skills.values_list('id', flat=True))
                completed_skill_ids = set(skills_with_questions)
                
                if required_skill_ids <= completed_skill_ids:
                    job_instance.job_creation_is_complete = True
                    job_instance.save()
                    logger.info(f"Job '{job_title}' marked as creation complete - all {len(required_skill_ids)} skills have questions")
                    
                    # Send notifications only once when job is fully complete
                    send_job_completion_notifications.delay(job_instance.id)
                else:
                    job_instance.save()  # Save progress update
                    missing_skills = required_skill_ids - completed_skill_ids
                    logger.info(f"Job '{job_title}' progress: {len(completed_skill_ids)}/{len(required_skill_ids)} skills complete")
                    
        except Exception as e:
            logger.error(f"Error checking job completion for '{job_title}': {e}")

    return {"success": success, "questions": serialized_questions}


def generate_mcqs_for_skill(skill_name, entry_level, job_title):
    conversation = [
        {
            "role": "user",
            "content": f'Generate a set of 10 technical multiple-choice questions and answers related to the skill of {skill_name}, specifically tailored for a {entry_level} {job_title} position. Ensure that the questions cover the five key interview areas most relevant for this role. Each question should be followed by four answer choices (A, B, C, D) and include a correct answer.\n\nThe response should be formatted in JSON, with each multiple-choice question represented as an object structured as follows:\n{{\n  "question": "",\n  "options": {{\n    "A": "",\n    "B": "",\n    "C": "",\n    "D": ""\n  }},\n  "correct_answer": "",\n  "area": ""\n}}\nPlease ensure that the area of expertise related to each question is also specified within the JSON object.',
        }
    ]

    try:
        response = client.chat.completions.create(model="gpt-4", messages=conversation, timeout=120)

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


# to send job emails to users


from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


@shared_task
def send_job_completion_notifications(job_id):
    """
    Send email notifications when a job creation is fully complete.
    This is called only once when all questions have been generated.
    """
    try:
        from .models import Job
        from messaging.tasks import send_recruiter_job_confirmation_email_task, send_new_job_email_task
        
        job_instance = Job.objects.get(id=job_id)
        
        # Send email to recruiter
        send_recruiter_job_confirmation_email_task.delay(
            email=job_instance.user.email,
            full_name=job_instance.user.get_full_name(),
            job_title=job_instance.title,
            company_name=job_instance.company.name,
            job_id=job_instance.id,
        )

        # Send email to users about the new job
        send_new_job_email_task.delay(
            email=job_instance.user.email,
            full_name=job_instance.user.get_full_name(),
            job_title=job_instance.title,
            job_link=f"https://umemployed.com/jobs/{job_instance.id}/",
            job_description=job_instance.description,
            company_name=job_instance.company.name,
            job_id=job_instance.id,
        )
        
        logger.info(f"Sent completion notifications for job '{job_instance.title}' (ID: {job_id})")
        
    except Job.DoesNotExist:
        logger.error(f"Job with ID {job_id} not found for notification sending")
    except Exception as e:
        logger.error(f"Error sending job completion notifications for job {job_id}: {e}")


@shared_task(bind=True, autoretry_for=(Exception,), retry_kwargs={'max_retries': 2, 'countdown': 300})
def smart_generate_questions_task(self, job_id, skill_id, entry_level, questions_per_skill=5):
    """
    Smart question generation with fallback strategies.
    
    Strategy:
    1. Try AI generation (up to 3 attempts with delays)
    2. If AI fails, use question pool
    3. If no pool questions, mark for manual review
    4. Always ensure job can be completed
    """
    from .models import Job, Skill, SkillQuestion, QuestionPool, SkillGenerationStatus
    from django.db import transaction
    from django.utils import timezone
    import time
    
    try:
        with transaction.atomic():
            job = Job.objects.get(id=job_id)
            skill = Skill.objects.get(id=skill_id)
            
            # Get or create status tracking
            status_obj, created = SkillGenerationStatus.objects.get_or_create(
                job=job,
                skill=skill,
                defaults={'status': 'pending'}
            )
            
            # Update status to in_progress
            status_obj.status = 'in_progress'
            status_obj.last_attempt_at = timezone.now()
            status_obj.save()
            
        logger.info(f"Starting smart question generation for {skill.name} in job {job.title}")
        
        # Check if questions already exist
        existing_count = SkillQuestion.objects.filter(job=job, skill=skill).count()
        if existing_count >= questions_per_skill:
            status_obj.status = 'ai_success'
            status_obj.questions_generated = existing_count
            status_obj.save()
            logger.info(f"Questions already exist for {skill.name}")
            return {"success": True, "source": "existing", "count": existing_count}
        
        # Strategy 1: Try AI Generation
        if status_obj.can_retry_ai():
            success, questions = try_ai_generation(job.title, entry_level, skill.name, questions_per_skill)
            status_obj.ai_attempts += 1
            
            if success and questions:
                # Save AI-generated questions
                created_count = save_questions_to_db(
                    questions, job, skill, entry_level, source='ai_generated'
                )
                
                status_obj.status = 'ai_success'
                status_obj.questions_generated = created_count
                status_obj.save()
                
                logger.info(f"AI generated {created_count} questions for {skill.name}")
                check_job_completion(job)
                return {"success": True, "source": "ai_generated", "count": created_count}
            else:
                status_obj.status = 'ai_failed'
                status_obj.error_message = "AI generation failed"
                status_obj.save()
        
        # Strategy 2: Use Question Pool
        if status_obj.should_use_fallback():
            fallback_count = use_fallback_questions(job, skill, entry_level, questions_per_skill)
            
            if fallback_count > 0:
                status_obj.status = 'fallback_used'
                status_obj.questions_generated = fallback_count
                status_obj.save()
                
                logger.info(f"Used {fallback_count} fallback questions for {skill.name}")
                check_job_completion(job)
                return {"success": True, "source": "fallback_pool", "count": fallback_count}
        
        # Strategy 3: Use Generic Questions (when no skill-specific pool exists)
        generic_count = use_generic_questions(job, skill, entry_level, questions_per_skill)
        
        if generic_count > 0:
            status_obj.status = 'generic_used'
            status_obj.questions_generated = generic_count
            status_obj.save()
            
            logger.info(f"Used {generic_count} generic questions for {skill.name}")
            check_job_completion(job)
            return {"success": True, "source": "generic", "count": generic_count}
        
        # Strategy 4: Create Experience-Based Questions
        experience_count = create_experience_questions(job, skill, entry_level)
        
        if experience_count > 0:
            status_obj.status = 'experience_based'
            status_obj.questions_generated = experience_count
            status_obj.save()
            
            logger.info(f"Created {experience_count} experience-based questions for {skill.name}")
            check_job_completion(job)
            return {"success": True, "source": "experience_based", "count": experience_count}
        
        # Strategy 5: Portfolio Review Only (final fallback)
        status_obj.status = 'portfolio_only'
        status_obj.save()
        
        logger.warning(f"No questions available for {skill.name} - marked as portfolio review only")
        check_job_completion(job, allow_partial=True)
        return {"success": True, "source": "portfolio_only", "count": 0}
        
    except Exception as e:
        logger.error(f"Error in smart question generation: {e}")
        if 'status_obj' in locals():
            status_obj.status = 'ai_failed'
            status_obj.error_message = str(e)
            status_obj.save()
        raise


def try_ai_generation(job_title, entry_level, skill_name, questions_per_skill):
    """Try to generate questions using AI"""
    try:
        question_data_list = generate_mcqs_for_skill(skill_name, entry_level, job_title)
        
        if question_data_list and isinstance(question_data_list, list):
            return True, question_data_list[:questions_per_skill]
        return False, []
    except Exception as e:
        logger.error(f"AI generation failed for {skill_name}: {e}")
        return False, []


def use_fallback_questions(job, skill, entry_level, questions_per_skill):
    """Use pre-made questions from the question pool"""
    from .models import QuestionPool, SkillQuestion
    
    # Map entry levels to difficulty
    difficulty_map = {
        'Beginner': 'beginner',
        'Mid': 'intermediate', 
        'Expert': 'advanced'
    }
    
    difficulty = difficulty_map.get(entry_level, 'intermediate')
    
    # Get questions from pool
    pool_questions = QuestionPool.objects.filter(
        skill=skill,
        difficulty=difficulty,
        is_active=True
    ).order_by('usage_count')[:questions_per_skill]
    
    if not pool_questions.exists():
        # Try any difficulty level for this skill
        pool_questions = QuestionPool.objects.filter(
            skill=skill,
            is_active=True
        ).order_by('usage_count')[:questions_per_skill]
    
    if not pool_questions.exists():
        return 0
    
    # Create SkillQuestion objects from pool
    questions_to_create = []
    for pool_q in pool_questions:
        questions_to_create.append(SkillQuestion(
            question=pool_q.question,
            option_a=pool_q.option_a,
            option_b=pool_q.option_b,
            option_c=pool_q.option_c,
            option_d=pool_q.option_d,
            correct_answer=pool_q.correct_answer,
            skill=skill,
            job=job,
            entry_level=entry_level,
            area=pool_q.area,
            source='fallback_pool'
        ))
        
        # Update usage count
        pool_q.usage_count += 1
        pool_q.save()
    
    created_questions = SkillQuestion.objects.bulk_create(
        questions_to_create, 
        ignore_conflicts=True
    )
    
    return len(created_questions)


def use_generic_questions(job, skill, entry_level, questions_per_skill):
    """
    Use generic programming/professional questions when no skill-specific pool exists.
    These are universal questions that apply to any tech role.
    """
    from .models import SkillQuestion
    
    # Generic questions that work for any skill
    generic_questions = [
        {
            "question": f"What is the most important principle when working with {skill.name}?",
            "option_a": "Writing clean, maintainable code",
            "option_b": "Optimizing for performance only",
            "option_c": "Using the latest features",
            "option_d": "Following team conventions",
            "correct_answer": "A",
            "area": "Best Practices"
        },
        {
            "question": f"When learning a new {skill.name} concept, what is the best approach?",
            "option_a": "Jump straight into complex projects",
            "option_b": "Start with documentation and simple examples",
            "option_c": "Copy code from tutorials without understanding",
            "option_d": "Ask others to do it for you",
            "correct_answer": "B",
            "area": "Learning Approach"
        },
        {
            "question": f"How do you typically debug issues in {skill.name}?",
            "option_a": "Random trial and error",
            "option_b": "Systematic debugging with tools and logs",
            "option_c": "Immediately ask for help",
            "option_d": "Restart everything",
            "correct_answer": "B",
            "area": "Problem Solving"
        },
        {
            "question": f"What is most important when collaborating on {skill.name} projects?",
            "option_a": "Working independently without communication",
            "option_b": "Clear documentation and version control",
            "option_c": "Using only your preferred tools",
            "option_d": "Avoiding code reviews",
            "correct_answer": "B",
            "area": "Collaboration"
        },
        {
            "question": f"How do you stay updated with {skill.name} developments?",
            "option_a": "Don't need to stay updated",
            "option_b": "Official documentation and community resources",
            "option_c": "Random blog posts only",
            "option_d": "Wait for others to tell me",
            "correct_answer": "B",
            "area": "Continuous Learning"
        }
    ]
    
    # Create questions (limit to requested amount)
    questions_to_create = []
    for i, q_data in enumerate(generic_questions[:questions_per_skill]):
        questions_to_create.append(SkillQuestion(
            question=q_data["question"],
            option_a=q_data["option_a"],
            option_b=q_data["option_b"],
            option_c=q_data["option_c"],
            option_d=q_data["option_d"],
            correct_answer=q_data["correct_answer"],
            skill=skill,
            job=job,
            entry_level=entry_level,
            area=q_data["area"],
            source='generic'
        ))
    
    if questions_to_create:
        created_questions = SkillQuestion.objects.bulk_create(
            questions_to_create, 
            ignore_conflicts=True
        )
        return len(created_questions)
    
    return 0


def create_experience_questions(job, skill, entry_level):
    """
    Create experience-based questions when all else fails.
    These focus on practical experience rather than technical knowledge.
    """
    from .models import SkillQuestion
    
    # Experience-based questions
    experience_questions = [
        {
            "question": f"How many years of experience do you have with {skill.name}?",
            "option_a": "Less than 1 year",
            "option_b": "1-3 years",
            "option_c": "3-5 years", 
            "option_d": "More than 5 years",
            "correct_answer": "B" if entry_level == "Mid" else "A" if entry_level == "Beginner" else "D",
            "area": "Experience Level"
        },
        {
            "question": f"Which best describes your {skill.name} project experience?",
            "option_a": "Only tutorials and learning projects",
            "option_b": "Personal projects and contributions",
            "option_c": "Professional projects in team environment",
            "option_d": "Leading {skill.name} projects and mentoring others",
            "correct_answer": "B" if entry_level == "Beginner" else "C" if entry_level == "Mid" else "D",
            "area": "Project Experience"
        },
        {
            "question": f"What type of {skill.name} projects have you worked on?",
            "option_a": "Simple scripts or basic implementations",
            "option_b": "Medium complexity applications",
            "option_c": "Large-scale production systems",
            "option_d": "Enterprise-level architecture and design",
            "correct_answer": "A" if entry_level == "Beginner" else "B" if entry_level == "Mid" else "C",
            "area": "Project Complexity"
        }
    ]
    
    questions_to_create = []
    for q_data in experience_questions:
        questions_to_create.append(SkillQuestion(
            question=q_data["question"],
            option_a=q_data["option_a"],
            option_b=q_data["option_b"],
            option_c=q_data["option_c"],
            option_d=q_data["option_d"],
            correct_answer=q_data["correct_answer"],
            skill=skill,
            job=job,
            entry_level=entry_level,
            area=q_data["area"],
            source='experience_based'
        ))
    
    if questions_to_create:
        created_questions = SkillQuestion.objects.bulk_create(
            questions_to_create, 
            ignore_conflicts=True
        )
        return len(created_questions)
    
    return 0


def check_job_completion(job, allow_partial=False):
    """
    Check if job can be marked as complete.
    
    Args:
        job: Job instance
        allow_partial: If True, allow completion with 80%+ skills having questions
    """
    from .models import SkillGenerationStatus
    from django.db import transaction
    
    with transaction.atomic():
        job = Job.objects.select_for_update().get(id=job.id)
        
        if job.job_creation_is_complete:
            return
        
        total_skills = job.requirements.count()
        if total_skills == 0:
            return
        
        # Count skills with questions or acceptable statuses
        acceptable_statuses = ['ai_success', 'fallback_used', 'generic_used', 'experience_based']
        if allow_partial:
            acceptable_statuses.append('portfolio_only')
        
        completed_skills = SkillGenerationStatus.objects.filter(
            job=job,
            status__in=acceptable_statuses
        ).count()
        
        # Check completion criteria
        completion_threshold = 0.8 if allow_partial else 1.0
        completion_ratio = completed_skills / total_skills
        
        if completion_ratio >= completion_threshold:
            job.job_creation_is_complete = True
            job.save()
            
            logger.info(f"Job '{job.title}' marked complete: {completed_skills}/{total_skills} skills ready")
            
            # Send notifications
            send_job_completion_notifications.delay(job.id)
        else:
            logger.info(f"Job '{job.title}' progress: {completed_skills}/{total_skills} skills ready ({completion_ratio*100:.1f}%)")


def save_questions_to_db(questions, job, skill, entry_level, source='ai_generated'):
    """Save questions to database"""
    from .models import SkillQuestion
    
    questions_to_create = []
    for question_data in questions:
        questions_to_create.append(SkillQuestion(
            question=question_data["question"],
            option_a=question_data["options"].get("A", ""),
            option_b=question_data["options"].get("B", ""),
            option_c=question_data["options"].get("C", ""),
            option_d=question_data["options"].get("D", ""),
            correct_answer=question_data["correct_answer"],
            skill=skill,
            job=job,
            entry_level=entry_level,
            area=question_data.get("area", ""),
            source=source
        ))
    
    created_questions = SkillQuestion.objects.bulk_create(
        questions_to_create, 
        ignore_conflicts=True
    )
    
    return len(created_questions)
