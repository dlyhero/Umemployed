import asyncio
import json
import logging
import os
import dotenv
import google.generativeai as genai
from google.generativeai import GenerativeModel
from openai import OpenAI
from django.http import JsonResponse
from django.utils.decorators import async_only_middleware
from asgiref.sync import sync_to_async
from .models import Skill, SkillQuestion

dotenv.load_dotenv()

# Global model initialization
genai_model = genai.GenerativeModel("gemini-1.5-flash")
# Configure the OpenAI client
api_key = os.environ.get('OPENAI_API_KEY')
openai_client = OpenAI(api_key=api_key)

# Configure the Gemini client
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

logger = logging.getLogger(__name__)

async def generate_questions_view(request):
    if request.method == 'GET':
        job_title = request.GET.get('job_title')
        entry_level = request.GET.get('entry_level')
        selected_skills = request.GET.get('selected_skills')
        selected_skill_names = selected_skills.split(',') if selected_skills else []

        try:
            questions_per_skill = 3
            all_questions = []

            for skill_name in selected_skill_names:
                questions = await generate_questions_for_skills(job_title, entry_level, skill_name, questions_per_skill)
                all_questions.extend(questions)

            if all_questions:
                serialized_questions = [{
                    'question': q.question,
                    'option_a': q.option_a,
                    'option_b': q.option_b,
                    'option_c': q.option_c,
                    'option_d': q.option_d,
                    'correct_answer': q.correct_answer,
                    'skill': q.skill.name,
                    'entry_level': q.entry_level
                } for q in all_questions]

                return JsonResponse(serialized_questions, safe=False)
            else:
                return JsonResponse({"error": "Failed to generate questions"}, status=500)

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return JsonResponse({"error": "An error occurred"}, status=500)

    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)

async def generate_questions_for_skills(job_title, entry_level, skill_name, questions_per_skill):
    skill = await sync_to_async(Skill.objects.get)(name=skill_name)
    questions = []

    for _ in range(questions_per_skill):
        question_data = await generate_mcqs_for_skill(skill_name)

        if question_data:
            skill_question = await sync_to_async(SkillQuestion.objects.create)(
                question=question_data['question'],
                option_a=question_data['options'].get('A', ''),
                option_b=question_data['options'].get('B', ''),
                option_c=question_data['options'].get('C', ''),
                option_d=question_data['options'].get('D', ''),
                correct_answer=question_data['correct_answer'],
                skill=skill,
                entry_level=entry_level
            )
            questions.append(skill_question)

    return questions

async def generate_mcqs_for_skill(skill_name):
    conversation = [
        {
            "role": "user",
            "content": f"Generate 5 technical multiple-choice questions related to the skill: {skill_name}. Each question should include four options (A, B, C, D) and the correct answer in JSON format."
        }
    ]

    logger.info(f"Querying for skill: {skill_name}")
    openai_response = None
    gemini_response = None

    try:
        openai_task = asyncio.create_task(query_openai(conversation))
        gemini_task = asyncio.create_task(query_gemini(conversation))

        # Use asyncio.wait to apply a timeout for each task
        done, pending = await asyncio.wait(
            [openai_task, gemini_task], return_when=asyncio.FIRST_COMPLETED, timeout=60
        )

        for task in done:
            if task == openai_task:
                openai_response = task.result()
            elif task == gemini_task:
                gemini_response = task.result()

        # Cancel any pending tasks
        for task in pending:
            task.cancel()

        # Return the first successful response
        if openai_response:
            logger.info(f"Received response from OpenAI: {openai_response}")
            return openai_response
        elif gemini_response:
            logger.info(f"Received response from Gemini: {gemini_response}")
            return gemini_response

    except asyncio.TimeoutError:
        logger.error("Timed out waiting for responses from both services.")
    except Exception as e:
        logger.error(f"Error occurred: {e}")

    logger.error("Failed to get a valid response from both OpenAI and Gemini")
    return None

async def query_openai(conversation):
    logger.info("Querying OpenAI with conversation: %s", conversation)

    try:
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: openai_client.chat.completions.create(
                model="gpt-4", 
                messages=conversation, 
                timeout=120
            )
        )

        content = response.choices[0].message.content
        mcqs_data = json.loads(content)

        if isinstance(mcqs_data, dict):
            return mcqs_data
        else:
            logger.error("Unexpected OpenAI response format: %s", mcqs_data)
            return None

    except json.JSONDecodeError as json_error:
        logger.error("JSON parsing failed: %s", json_error)
    except ConnectionError as conn_error:
        logger.error("Network issue: %s", conn_error)
    except Exception as e:
        logger.exception("Unexpected error querying OpenAI: %s", e)

    return None

async def query_gemini(conversation):
    logger.info("Querying Gemini with conversation: %s", conversation)

    try:
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: genai_model.generate_content(
                conversation[0]["content"]
            )
        )

        logger.info("Gemini raw response: %s", response)

        if hasattr(response, 'result') and response.result.candidates:
            candidate_content = response.result.candidates[0].content
            
            if hasattr(candidate_content, 'parts') and candidate_content.parts:
                mcqs_data = candidate_content.parts[0].text
                logger.info("Gemini candidate content: %s", mcqs_data)
                
                # Try to parse the response as JSON
                mcqs_and_answers_list = json.loads(mcqs_data)

                if isinstance(mcqs_and_answers_list, list):
                    return mcqs_and_answers_list
                else:
                    logger.error("Unexpected format for Gemini response: %s", mcqs_and_answers_list)
                    return None
            else:
                logger.error("No parts found in the candidate content.")
                return None
        else:
            logger.error("No candidates found in the response.")
            return None

    except json.JSONDecodeError as json_error:
        logger.error("JSON decode error: %s", json_error)
        return None
    except Exception as e:
        logger.error(f"Error querying Gemini: {e}")
        return None