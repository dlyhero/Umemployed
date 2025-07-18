import json
import logging

import openai
from celery import shared_task
from django.conf import settings
from django.contrib.auth.models import User

from job.models import Job

from .models import EnhancedResume, ResumeDoc, ResumeEnhancementTask

logger = logging.getLogger(__name__)


@shared_task(
    bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 60}
)
def process_resume_upload_task(self, user_id, resume_doc_id, extracted_text):
    """
    Celery task to process resume upload asynchronously.
    
    This task handles the time-consuming OpenAI API calls for resume analysis
    to prevent timeout issues in the web request.
    
    Args:
        user_id: ID of the user
        resume_doc_id: ID of the ResumeDoc record
        extracted_text: Extracted text from the resume
        
    Returns:
        dict: Status and result information
    """
    try:
        from .extract_pdf import extract_resume_details, parse_and_save_details, extract_technical_skills
        
        # Get user and resume doc objects
        user = User.objects.get(id=user_id)
        resume_doc = ResumeDoc.objects.get(id=resume_doc_id, user=user)
        
        # Step 1: Extract resume details using OpenAI
        logger.info(f"Starting resume details extraction for user {user_id}")
        extracted_details = extract_resume_details(user, extracted_text)
        
        # Step 2: Parse and save details to database
        logger.info(f"Parsing and saving resume details for user {user_id}")
        parse_and_save_details(extracted_details, user)
        
        # Step 3: Extract technical skills
        logger.info(f"Extracting technical skills for user {user_id}")
        job_title = "Others"  # Default job title
        technical_skills = extract_technical_skills(user, extracted_text, job_title)
        
        # Step 4: Update resume doc with extracted text and skills
        resume_doc.extracted_text = extracted_text
        resume_doc.save()
        
        logger.info(f"Resume processing completed successfully for user {user_id}")
        
        return {
            "status": "success",
            "extracted_details": extracted_details,
            "technical_skills": technical_skills,
            "message": "Resume processed successfully"
        }
        
    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} not found")
        return {"status": "failed", "error": "User not found"}
    except ResumeDoc.DoesNotExist:
        logger.error(f"ResumeDoc with ID {resume_doc_id} not found for user {user_id}")
        return {"status": "failed", "error": "Resume document not found"}
    except Exception as e:
        logger.error(f"Unexpected error in resume processing: {str(e)}")
        
        # If this is a retry, we'll let Celery handle it
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60, exc=e)
        return {"status": "failed", "error": str(e)}


@shared_task(
    bind=True, autoretry_for=(Exception,), retry_kwargs={"max_retries": 3, "countdown": 60}
)
def enhance_resume_task(self, user_id, job_id, resume_text, task_record_id):
    """
    Celery task to enhance a resume using AI.

    Args:
        user_id: ID of the user
        job_id: ID of the job to tailor the resume for
        resume_text: Extracted text from the resume
        task_record_id: ID of the ResumeEnhancementTask record

    Returns:
        dict: Status and result information
    """
    try:
        # Update task status to processing
        task_record = ResumeEnhancementTask.objects.get(id=task_record_id)
        task_record.status = "processing"
        task_record.save()

        # Get user and job objects
        user = User.objects.get(id=user_id)
        job = Job.objects.get(id=job_id)
        job_description = str(job.description)

        # Prepare AI prompts
        section_str = "full_name, email, phone, linkedin, location, summary, skills, experience, education, certifications"

        system_prompt = (
            "YOU ARE A WORLD-CLASS RESUME ENHANCEMENT AGENT SPECIALIZED IN TAILORING RESUMES TO MATCH SPECIFIC JOB DESCRIPTIONS. "
            "YOUR TASK IS TO TRANSFORM A PARSED RESUME TO ALIGN PERFECTLY WITH THE PROVIDED JOB DESCRIPTION, OPTIMIZING FOR ATS (APPLICANT TRACKING SYSTEM) PARSING AND RELEVANCY.\n\n"
            "###INSTRUCTIONS###\n"
            "UPDATE ONLY THE SUMMARY AND EXPERIENCE SECTIONS BASED ON THE JOB DESCRIPTION,\n"
            f"ENSURE THE FINAL RESUME INCLUDES ONLY THE FOLLOWING SECTIONS: {section_str},\n"
            "FORMAT OUTPUT USING ATS-COMPATIBLE STRUCTURE: clean headings, no graphics/tables, consistent formatting,\n"
            "INTEGRATE RELEVANT KEYWORDS, SKILLS, TOOLS, AND PHRASES DIRECTLY FROM THE JOB DESCRIPTION,\n"
            "PRESERVE THE CANDIDATE'S ORIGINAL ACCOMPLISHMENTS WHILE REPHRASING TO ALIGN WITH JOB REQUIREMENTS,\n"
            "MAINTAIN PROFESSIONAL, CONCISE LANGUAGE FOCUSED ON IMPACT AND RESULTS,\n"
            "FOR THE 'skills' SECTION, GROUP/CATEGORIZE THE SKILLS INTO RELEVANT CATEGORIES (e.g., 'Programming Languages', 'Machine Learning', 'Software', etc.) "
            "AND RETURN THEM AS AN OBJECT WHERE EACH KEY IS A CATEGORY AND THE VALUE IS A LIST OF SKILLS IN THAT CATEGORY. "
            'EXAMPLE: {"Programming Languages": ["Python", "SQL"], "Machine Learning": ["KNN", "XGBoost"]}\n'
            "FOR THE 'education' SECTION, RETURN A LIST OF ALL EDUCATION ENTRIES FOUND, NOT JUST ONE. "
            "FOR THE 'experience' SECTION, RETURN A LIST OF ALL WORK EXPERIENCE ENTRIES FOUND, NOT JUST ONE. "
            "FOR THE 'certifications' SECTION, RETURN A LIST OF ALL CERTIFICATIONS FOUND, NOT JUST ONE. "
            "EACH ENTRY IN 'education', 'experience', or 'certifications' SHOULD BE AN OBJECT WITH RELEVANT FIELDS (e.g., institution, degree, years for education; company, role, dates for experience; name, issuer, year for certifications).\n\n"
            "###CHAIN OF THOUGHTS###\n"
            "UNDERSTAND: READ AND COMPREHEND BOTH THE PARSED RESUME AND JOB DESCRIPTION,\n"
            "BASICS: IDENTIFY THE JOB TITLE, KEY RESPONSIBILITIES, REQUIRED SKILLS, AND INDUSTRY CONTEXT,\n"
            "BREAK DOWN: DECONSTRUCT THE JOB DESCRIPTION INTO A LIST OF DESIRED QUALIFICATIONS, TOOLS, AND EXPERIENCES,\n"
            "ANALYZE: COMPARE THE JOB REQUIREMENTS TO THE CANDIDATE'S EXPERIENCE, IDENTIFYING ALIGNMENT AND GAPS,\n"
            "BUILD: REWRITE THE SUMMARY TO EMPHASIZE RELEVANT SKILLS, TOOLS, AND INDUSTRY EXPERIENCE\n"
            "REWRITE EACH BULLET IN THE EXPERIENCE SECTION TO HIGHLIGHT MATCHING SKILLS AND IMPACT,\n"
            "EDGE CASES: IF A MATCHING TOOL/SKILL IS MISSING, PRIORITIZE GENERAL BUT RELATED TRANSFERABLE LANGUAGE,\n"
            f"FINAL ANSWER: RETURN ONLY THE UPDATED RESUME CONTAINING SECTIONS: {section_str},\n\n"
            "###WHAT NOT TO DO###\n"
            f"NEVER INCLUDE SECTIONS OUTSIDE THE ALLOWED LIST: {section_str},\n"
            "NEVER COPY-PASTE LARGE CHUNKS FROM THE JOB DESCRIPTION WITHOUT ADAPTATION,\n"
            'NEVER USE GENERIC, VAGUE LANGUAGE (E.G., "responsible for", "worked on"),\n'
            "NEVER INCLUDE GRAPHICS, COLUMNS, IMAGES, OR TABLES (NON-ATS COMPATIBLE),\n"
            "NEVER OMIT RELEVANT KEYWORDS OR INDUSTRY TERMINOLOGY FOUND IN THE JOB DESCRIPTION,\n"
            "NEVER INTRODUCE FABRICATED INFORMATION OR FAKE EXPERIENCES,\n\n"
            "###FEW-SHOT EXAMPLES###\n"
            "Original Experience Bullet:\n"
            "Led a team of developers to build internal tools.\n\n"
            "Job Description Requirement:\n"
            "Experience with Agile methodologies and CI/CD pipelines.\n\n"
            "Optimized Bullet:\n"
            "Led a cross-functional Agile team to develop internal tools, integrating CI/CD pipelines for accelerated deployment cycles.\n"
        )

        user_prompt = (
            "Given the following resume text and job description, rewrite and enhance the resume so that it is smooth, well-structured, "
            "and tailored to match the job description as closely as possible. "
            "Ensure the resume highlights relevant skills, experience, and qualifications that fit the job. "
            "Return only a valid JSON object with the allowed sections.\n\n"
            f"Resume Text:\n{resume_text}\n\n"
            f"Job Description:\n{job_description}\n"
        )

        # Call OpenAI API
        openai.api_key = getattr(settings, "OPENAI_API_KEY", None)
        client = openai.OpenAI(api_key=openai.api_key)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=1500,
            temperature=0.7,
        )

        ai_content = response.choices[0].message.content
        enhanced_resume = json.loads(ai_content)

        # Save the enhanced resume
        skills = enhanced_resume.get("skills", {})

        # Create new enhanced resume record
        enhanced_resume_obj = EnhancedResume.objects.create(
            user=user,
            job=job,
            full_name=enhanced_resume.get("full_name"),
            email=enhanced_resume.get("email"),
            phone=enhanced_resume.get("phone"),
            linkedin=enhanced_resume.get("linkedin"),
            location=enhanced_resume.get("location"),
            summary=enhanced_resume.get("summary"),
            skills=skills,
            experience=enhanced_resume.get("experience"),
            education=enhanced_resume.get("education"),
        )

        # Update task record with completion
        task_record.status = "completed"
        task_record.enhanced_resume = enhanced_resume_obj
        task_record.save()

        logger.info(f"Resume enhancement completed successfully for user {user_id}, job {job_id}")

        return {
            "status": "success",
            "enhanced_resume": enhanced_resume,
            "enhanced_resume_id": enhanced_resume_obj.id,
        }

    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error in resume enhancement: {str(e)}")
        task_record = ResumeEnhancementTask.objects.get(id=task_record_id)
        task_record.status = "failed"
        task_record.error_message = f"AI response could not be parsed as JSON: {str(e)}"
        task_record.save()
        return {"status": "failed", "error": f"AI response could not be parsed as JSON: {str(e)}"}
    except User.DoesNotExist:
        logger.error(f"User with ID {user_id} not found")
        task_record = ResumeEnhancementTask.objects.get(id=task_record_id)
        task_record.status = "failed"
        task_record.error_message = "User not found"
        task_record.save()
        return {"status": "failed", "error": "User not found"}
    except Job.DoesNotExist:
        logger.error(f"Job with ID {job_id} not found")
        task_record = ResumeEnhancementTask.objects.get(id=task_record_id)
        task_record.status = "failed"
        task_record.error_message = "Job not found"
        task_record.save()
        return {"status": "failed", "error": "Job not found"}
    except Exception as e:
        logger.error(f"Unexpected error in resume enhancement: {str(e)}")
        try:
            task_record = ResumeEnhancementTask.objects.get(id=task_record_id)
            task_record.status = "failed"
            task_record.error_message = str(e)
            task_record.save()
        except:
            pass  # Don't fail if we can't update the task record

        # If this is a retry, we'll let Celery handle it
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60, exc=e)
        return {"status": "failed", "error": str(e)}
