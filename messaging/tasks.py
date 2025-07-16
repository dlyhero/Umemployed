import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


@shared_task
def send_message_email_task(email, sender_name, message_text, conversation_id):
    subject = f"New Message from {sender_name}"
    message = f"You have received a new message from {sender_name}:\n\n{message_text}\n\nView the conversation: {settings.SITE_URL}/messaging/chat/{conversation_id}/"
    from_email = settings.DEFAULT_FROM_EMAIL

    try:
        send_mail(subject, message, from_email, [email])
    except Exception as e:
        logger.error(f"An error occurred while sending email to {email}: {e}")


@shared_task
def send_new_job_email_task(
    email, full_name, job_title, job_link, job_description, company_name, job_id
):
    """Send email notification to users about a new job posting"""
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
        logger.info(f"Successfully sent new job email to {email} for job '{job_title}'")
    except Exception as e:
        logger.error(f"An error occurred while sending new job email to {email}: {e}")


@shared_task(autoretry_for=(), max_retries=0)
def send_recruiter_job_confirmation_email_task(email, full_name, job_title, company_name, job_id):
    """Send confirmation email to recruiter when job is successfully created"""
    subject = f"Job Created Successfully: {job_title}"
    message = f"Hello {full_name},\n\nYour job '{job_title}' has been successfully created and is now available on the platform at {company_name}.\n\nBest regards,\nUmEmployed Team"
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
        logger.info(f"Successfully sent job confirmation email to {email} for job '{job_title}'")
    except Exception as e:
        logger.error(f"An error occurred while sending job confirmation email to {email}: {e}")
