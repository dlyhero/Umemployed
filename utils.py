import asyncio
from concurrent.futures import ThreadPoolExecutor
import aiohttp
from langchain_openai import ChatOpenAI
import os
import google.generativeai as genai
from google.generativeai import GenerativeModel

import json
from llamaapi import LlamaAPI
from llama_index.core.llms import ChatMessage



API_KEY="AIzaSyDDp5AwVk8ML1E0DDGzo2Lfh7GYzX9Jfdc"
genai.configure(api_key=API_KEY)


# Initialize ChatGPT (OpenAI) model
chatgpt_model = ChatOpenAI(
    openai_api_key="sk-RvKtbSmHPKtNw1txXl2xPMWE9-IxKxiYrLrhwvPljAT3BlbkFJ6TdK0vyrDokGGgNexAl_j1nM-SvsL0bGS_PzoObnUA", 
    model_name="gpt-4"
)

# Function to call ChatGPT (OpenAI GPT-4) using LangChain
async def call_chatgpt(prompt):
    response = chatgpt_model([{"role": "user", "content": prompt}])
    return response.content

# Function to call Gemini API
async def call_gemini(prompt):
    model = genai.GenerativeModel("gemini-1.5-flash")

    response = model.generate_content(prompt)
    return response.text

# Function to call LLaMA
async def call_llama(prompt):
    llama = LlamaAPI("LA-1b48b5dccbdd4c909012320b2b546528cd677192dc9e4a4dbcd9b3b28fb3ca0d")
    messages = [
    ChatMessage(
        role="system", content="Testing assessment questions generator"
    ),
    ChatMessage(role="user", content=prompt),]
    response = llama.chat(messages)
    return response

# Main function to handle the first completed API call
async def extract_information(prompt):
    # Use asyncio.gather with FIRST_COMPLETED option
    tasks = [
        call_chatgpt(prompt),
        call_gemini(prompt)
        # call_llama(prompt)
    ]

    # Wait for the first task to complete
    done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)

    # Get the first completed result
    first_completed_response = list(done)[0].result()

    # Store other responses (cancel if they are still pending)
    other_responses = []
    for task in pending:
        task.cancel()  # Cancel pending tasks
    for completed_task in done:
        other_responses.append(completed_task.result())

    return {
        "first_response": first_completed_response,
        "other_responses": other_responses
    }

# Example usage
async def main():
    prompt ='''Generate a set of 10 technical multiple-choice questions and answers related to the skill of electrical engineering, specifically tailored for a mid-level DOT Engineer position. Ensure that the questions cover the five key interview areas most relevant for this role. Each question should be followed by four answer choices (A, B, C, D) and include a correct answer.

The response should be formatted in JSON, with each multiple-choice question represented as an object structured as follows:
{
  "question": "",
  "options": {
    "A": "",
    "B": "",
    "C": "",
    "D": ""
  },
  "correct_answer": "",
  "area": ""
}
Please ensure that the area of expertise related to each question is also specified within the JSON object.'''
    result = await extract_information(prompt)

    print("First completed response:", result['first_response'])
    print("Other responses:", result['other_responses'])

# Run the asyncio event loop
asyncio.run(main())