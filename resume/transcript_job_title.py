import os
import logging
import pdfplumber
import io
from openai import OpenAI
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .forms import TranscriptForm
from .models import Transcript
from django.contrib import messages
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError


# Load environment variables
api_key = os.environ.get('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)
logger = logging.getLogger(__name__)

@login_required(login_url='login')
def upload_transcript(request):
    if request.method == 'POST':
        form = TranscriptForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_file = form.cleaned_data['file']
            blob_name = f"transcripts/{uploaded_file.name}"  # Construct the blob name

            # Upload the file to Azure Blob Storage
            account_name = os.getenv('AZURE_ACCOUNT_NAME')
            account_key = os.getenv('AZURE_ACCOUNT_KEY')
            container_name = os.getenv('AZURE_CONTAINER')

            connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)

            try:
                blob_client.upload_blob(uploaded_file)
                logger.info(f"File uploaded to Azure Blob Storage. Blob name: {blob_name}")
            except Exception as e:
                logger.error(f"Error uploading file to Azure Blob Storage: {str(e)}")
                messages.error(request, "An error occurred while uploading the file. Please try again.")
                return redirect('upload_transcript')

            # Create the Transcript object with the correct blob name
            transcript = Transcript.objects.create(
                user=request.user,
                file=blob_name,  # Store only the blob name
                extracted_text=''
            )

            # Redirect to the extraction view
            redirect_url = reverse('extract_transcript_text', kwargs={'file_path': blob_name})
            return redirect(redirect_url)
        else:
            messages.error(request, 'Invalid form submission. Please try again.')
            return redirect('upload_transcript')
    else:
        form = TranscriptForm()
    return render(request, 'resume/transcript/upload_transcript.html', {'form': form})


def extract_transcript_text(request, file_path):
    account_name = os.getenv('AZURE_ACCOUNT_NAME')
    account_key = os.getenv('AZURE_ACCOUNT_KEY')
    container_name = os.getenv('AZURE_CONTAINER')

    connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    
    # Use the file_path directly as the blob name
    blob_name = file_path
    logger.info(f"Blob name: {blob_name}")  # Log the blob name

    try:
        # Check if the transcript already exists in the database
        transcript = Transcript.objects.filter(user=request.user, file=file_path).first()
        if not transcript:
            transcript = Transcript.objects.create(user=request.user, file=file_path, extracted_text='')

        if transcript.extracted_text and transcript.reasoning:  # Check if both extracted text and reasoning exist
            extracted_text = transcript.extracted_text
            reasoning = transcript.reasoning
            logger.info("Using existing extracted text and reasoning.")
        else:
            # Download the file from Azure Blob Storage
            blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
            
            if not blob_client.exists():
                logger.error(f"Blob {blob_name} does not exist in container {container_name}.")
                messages.error(request, "The specified file does not exist.")
                return HttpResponse("Error: The specified file does not exist.", status=404)

            file_stream = blob_client.download_blob().readall()
            logger.info(f"File stream size: {len(file_stream)} bytes")

            # Extract text based on file extension
            file_extension = os.path.splitext(blob_name)[1].lower()
            extracted_text = ""

            if file_extension == '.pdf':
                with pdfplumber.open(io.BytesIO(file_stream)) as pdf:
                    if pdf.pages:
                        page = pdf.pages[0]
                        extracted_text = page.extract_text() or ""
                        logger.info(f"Extracted text from PDF: {extracted_text[:500]}")
            elif file_extension == '.txt':
                extracted_text = file_stream.decode('utf-8')
                logger.info(f"Extracted text from TXT: {extracted_text[:500]}")
            else:
                logger.error(f"Unsupported file extension: {file_extension}")
                messages.error(request, "Unsupported file type.")
                return HttpResponse("Unsupported file type", status=400)

            # Clean and save the extracted text
            extracted_text = extracted_text.replace('\x00', '') if extracted_text else extracted_text
            transcript.extracted_text = extracted_text

            # Get the perfect job title and reasoning using OpenAI
            job_title, reasoning = get_perfect_job_title_and_reasoning(extracted_text)

            # Save the reasoning in the database
            transcript.reasoning = reasoning
            transcript.save()

        # Return the job title and reasoning in the JSON response
        return JsonResponse({'job_title': job_title, 'reasoning': reasoning})

    except ResourceNotFoundError:
        logger.error(f"Blob {blob_name} not found in container {container_name}.")
        messages.error(request, "The specified file does not exist.")
        return HttpResponse("Error: The specified file does not exist.", status=404)
    except Exception as e:
        logger.error("Error during file extraction: %s", str(e), exc_info=True)
        messages.error(request, "An error occurred while processing the transcript. Please try again.")
        return HttpResponse("Error: Could not process the file", status=500)

def get_perfect_job_title_and_reasoning(extracted_text):
    """
    Uses OpenAI to suggest a job title and provide concise reasoning (50-75 words) based on the extracted transcript text.
    The LLM is instructed to choose only one best job title.
    """
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    conversation = [
        {
            "role": "user",
            "content": f"""
            Given the following transcript details: {extracted_text}, suggest the **one best job title** for the student based on their academic performance and courses taken. 
            The job title should be relevant to their field of study and skills. Ignore the program or degree mentioned in the transcript.
            Provide a concise reasoning (50-75 words) for why this job title is the best fit.
            Format your response as:
            Job Title: [Title]
            Reasoning: [Reasoning]
            """
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4",
        messages=conversation,
        timeout=120
    )

    response_content = response.choices[0].message.content

    # Split the response into job title and reasoning
    if "Job Title:" in response_content and "Reasoning:" in response_content:
        job_title = response_content.split("Job Title:")[1].split("Reasoning:")[0].strip()
        reasoning = response_content.split("Reasoning:")[1].strip()
    else:
        # Fallback if the response format is unexpected
        job_title = response_content
        reasoning = "No specific reasoning provided."

    return job_title, reasoning