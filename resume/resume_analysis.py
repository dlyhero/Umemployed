from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import ResumeDoc, ResumeAnalysis
from .extract_pdf import extract_text
from .forms import ResumeForm, Resume
import json
import dotenv
from openai import OpenAI
import os

import logging

dotenv.load_dotenv()
api_key = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)
logger = logging.getLogger(__name__)

@login_required(login_url='login')
def analyze_resume_view(request):
    """
    Handles the resume analysis workflow.
    """
    if request.method == 'POST':
        form = ResumeForm(request.POST, request.FILES)  # Use the imported ResumeForm
        if form.is_valid():
            # Check if a ResumeDoc already exists for the user
            try:
                resume_doc = ResumeDoc.objects.get(user=request.user)
                resume_doc.file = form.cleaned_data['file']
                resume_doc.extracted_text = ''
                resume_doc.extracted_skills.clear()
                resume_doc.save()
            except ResumeDoc.DoesNotExist:
                # Create a new ResumeDoc if it does not exist
                resume_doc = ResumeDoc.objects.create(
                    user=request.user,
                    file=form.cleaned_data['file']
                )

            # Extract text from the new resume
            file_path = resume_doc.file.url.lstrip('/')
            extract_text(request, file_path)
            resume_doc.refresh_from_db()  # Refresh to get the updated extracted_text

            # Analyze the resume text
            analysis_results = analyze_resume(resume_doc.extracted_text)

            # Save the analysis results to the database
            ResumeAnalysis.objects.create(
                user=request.user,
                resume=resume_doc,
                overall_score=analysis_results['overall_score'],
                criteria_scores=analysis_results['criteria_scores'],
                improvement_suggestions=analysis_results['improvement_suggestions']
            )

            # Redirect to the results page
            return JsonResponse({'status': 'success', 'redirect_url': reverse('resume_analysis')})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid file format.'}, status=400)
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=405)
    
def analyze_resume(extracted_text):
    """
    Analyzes the resume text based on the 15 criteria and returns the results.
    """
    system_prompt = """YOU ARE A WORLD-CLASS RESUME ANALYST AND CAREER COACH, SPECIALIZED IN EVALUATING AND OPTIMIZING RESUMES TO MAXIMIZE THEIR IMPACT. YOUR TASK IS TO ANALYZE THE GIVEN RESUME TEXT BASED ON 15 CRUCIAL CRITERIA AND PROVIDE A DETAILED ASSESSMENT WITH AN OVERALL SCORE OUT OF 100.

                ### INSTRUCTIONS ###
                - YOU MUST ANALYZE THE RESUME BASED ON THE FOLLOWING 15 CRITERIA:
                  1. **STRUCTURE & FORMATTING** (Is the resume well-organized and formatted for readability?)  
                  2. **CLARITY & CONCISENESS** (Is the information clear and to the point?)  
                  3. **PROFESSIONAL TONE** (Does the resume maintain a professional tone?)  
                  4. **GRAMMAR & SPELLING** (Are there any grammar, spelling, or punctuation mistakes?)  
                  5. **ACHIEVEMENTS & METRICS** (Does the resume use quantified achievements?)  
                  6. **RELEVANCE TO JOB** (Are skills and experiences aligned with target roles?)  
                  7. **KEYWORDS & ATS OPTIMIZATION** (Does the resume contain relevant industry keywords for ATS compatibility?)  
                  8. **WORK EXPERIENCE DETAIL** (Is work experience well-detailed and impactful?)  
                  9. **EDUCATION & CERTIFICATIONS** (Are education and certifications clearly stated?)  
                  10. **SKILLS SECTION EFFECTIVENESS** (Are the listed skills relevant and well-presented?)  
                  11. **ACTION VERBS & LANGUAGE** (Are strong action verbs used to describe experience?)  
                  12. **CONSISTENCY & FLOW** (Is the information presented in a logical and smooth manner?)  
                  13. **CONTACT INFORMATION COMPLETENESS** (Does it include essential contact details?)  
                  14. **CUSTOMIZATION FOR SPECIFIC JOB** (Is the resume tailored to a specific job or generic?)  
                  15. **OVERALL IMPACT & READABILITY** (Does the resume make a strong impression?)  

                - YOU MUST PROVIDE A SCORE FROM 0 TO 10 FOR EACH CRITERION  
                - THE FINAL SCORE MUST BE A WEIGHTED AVERAGE OF ALL 15 SCORES, OUT OF 100  
                - OUTPUT THE RESULTS IN A JSON FORMAT AS FOLLOWS:

                ### JSON OUTPUT FORMAT ###
                json
                {
                  "overall_score": <FINAL_SCORE_OUT_OF_100>,
                  "criteria_scores": {
                    "structure_formatting": <SCORE_OUT_OF_10>,
                    "clarity_conciseness": <SCORE_OUT_OF_10>,
                    "professional_tone": <SCORE_OUT_OF_10>,
                    "grammar_spelling": <SCORE_OUT_OF_10>,
                    "achievements_metrics": <SCORE_OUT_OF_10>,
                    "relevance_to_job": <SCORE_OUT_OF_10>,
                    "keywords_ats_optimization": <SCORE_OUT_OF_10>,
                    "work_experience_detail": <SCORE_OUT_OF_10>,
                    "education_certifications": <SCORE_OUT_OF_10>,
                    "skills_section_effectiveness": <SCORE_OUT_OF_10>,
                    "action_verbs_language": <SCORE_OUT_OF_10>,
                    "consistency_flow": <SCORE_OUT_OF_10>,
                    "contact_information_completeness": <SCORE_OUT_OF_10>,
                    "customization_for_specific_job": <SCORE_OUT_OF_10>,
                    "overall_impact_readability": <SCORE_OUT_OF_10>
                  },
                  "improvement_suggestions": {
                    "structure_formatting": "<SUGGESTIONS_FOR_IMPROVEMENT>",
                    "clarity_conciseness": "<SUGGESTIONS_FOR_IMPROVEMENT>",
                    "professional_tone": "<SUGGESTIONS_FOR_IMPROVEMENT>",
                    "grammar_spelling": "<SUGGESTIONS_FOR_IMPROVEMENT>",
                    "achievements_metrics": "<SUGGESTIONS_FOR_IMPROVEMENT>",
                    "relevance_to_job": "<SUGGESTIONS_FOR_IMPROVEMENT>",
                    "keywords_ats_optimization": "<SUGGESTIONS_FOR_IMPROVEMENT>",
                    "work_experience_detail": "<SUGGESTIONS_FOR_IMPROVEMENT>",
                    "education_certifications": "<SUGGESTIONS_FOR_IMPROVEMENT>",
                    "skills_section_effectiveness": "<SUGGESTIONS_FOR_IMPROVEMENT>",
                    "action_verbs_language": "<SUGGESTIONS_FOR_IMPROVEMENT>",
                    "consistency_flow": "<SUGGESTIONS_FOR_IMPROVEMENT>",
                    "contact_information_completeness": "<SUGGESTIONS_FOR_IMPROVEMENT>",
                    "customization_for_specific_job": "<SUGGESTIONS_FOR_IMPROVEMENT>",
                    "overall_impact_readability": "<SUGGESTIONS_FOR_IMPROVEMENT>"
                  }
                }
                """

    conversation = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Analyze the following resume text:\n\n{extracted_text}"}
    ]

    try:
        # Call GPT-4 to analyze the resume
        response = client.chat.completions.create(
            model="gpt-4",
            messages=conversation,
            timeout=120
        )

        # Parse the response
        response_content = response.choices[0].message.content
        analysis_results = json.loads(response_content)
        return analysis_results

    except Exception as e:
        logger.error(f"Error analyzing resume: {e}")
        return {
            "overall_score": 0,
            "criteria_scores": {},
            "improvement_suggestions": {}
        }

@login_required(login_url='login')
def resume_analysis(request):
    """
    Displays the resume analysis results.
    """
    try:
        # Get the latest analysis for the user
        latest_analysis = ResumeAnalysis.objects.filter(user=request.user).latest('analyzed_at')
        return render(request, 'resume/resume_analysis.html', {'analysis': latest_analysis})
    except ResumeAnalysis.DoesNotExist:
        messages.error(request, "No analysis found. Please analyze your resume first.")
        return redirect('analyze_resume')