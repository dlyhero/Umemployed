import threading
from datetime import datetime

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.template.loader import render_to_string


def send_email(subject, plain_message, from_email, recipient_list, html_message=None):
    email = EmailMultiAlternatives(
        subject=subject,
        body=plain_message,  # The plain text content
        from_email=from_email,
        to=recipient_list,
    )
    if html_message:
        email.attach_alternative(html_message, "text/html")  # Attach the HTML version
    email.send(fail_silently=False)


def send_welcome_email(user_email, user_name):
    subject = "Welcome to Our Service"
    plain_message = f"Hello {user_name},\n\nThank you for registering."
    html_message = render_to_string(
        "emails/welcome.html", {"user": user_name, "message": "Thank you for registering."}
    )
    thread = threading.Thread(
        target=send_email,
        args=(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [user_email], html_message),
    )
    thread.start()


def send_login_email(user_email, user_name):
    subject = "Welcome Back to UmEmployed"
    plain_message = f"Hello {user_name},\n\nWelcome back to UmEmployed."
    html_message = render_to_string("emails/welcome_back.html", {"user": user_name})
    thread = threading.Thread(
        target=send_email,
        args=(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [user_email], html_message),
    )
    thread.start()


def send_logout_email(user_email, user_name):
    subject = "See You Soon at UmEmployed!"
    plain_message = f"Goodbye {user_name},\n\nSee you soon at UmEmployed!"
    html_message = render_to_string("emails/logout.html", {"user": user_name})
    thread = threading.Thread(
        target=send_email,
        args=(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [user_email], html_message),
    )
    thread.start()


def send_password_reset_email(user_email, user_name):
    subject = "Password Reset Successful"
    plain_message = f"Hello {user_name},\n\nYour password has been reset successfully."
    html_message = render_to_string(
        "emails/password_reset.html",
        {"user": user_name, "message": "Your password has been reset successfully."},
    )
    thread = threading.Thread(
        target=send_email,
        args=(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [user_email], html_message),
    )
    thread.start()


def send_new_job_email(user_email, user_name, job_title, job_link, job_description, company):
    subject = "New Job Posted: {}".format(job_title)
    plain_message = f"Hello {user_name},\n\nA new job titled '{job_title}' has been posted by {company}.\nYou can view the job details here: {job_link}\n\nJob Description: {job_description}\n\nBest Regards,\nYour Application System"

    html_message = render_to_string(
        "emails/new_job.html",
        {
            "user": user_name,
            "company": company,
            "job_title": job_title,
            "job_link": job_link,
            "job_description": job_description,
            "current_year": datetime.now().year,
        },
    )
    thread = threading.Thread(
        target=send_email,
        args=(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [user_email], html_message),
    )
    thread.start()


def send_application_email(recruiter_email, applicant_name, job_title, job_link):
    subject = "New Job Application: {}".format(job_title)
    plain_message = f"Hello,\n\n{applicant_name} has applied for the job '{job_title}'.\nYou can view the job details here: {job_link}\n\nBest Regards,\nYour Application System"

    html_message = render_to_string(
        "emails/job_application.html",
        {
            "applicant_name": applicant_name,
            "job_title": job_title,
            "job_link": job_link,
            "current_year": datetime.now().year,
        },
    )

    thread = threading.Thread(
        target=send_email,
        args=(subject, plain_message, settings.DEFAULT_FROM_EMAIL, [recruiter_email], html_message),
    )
    thread.start()
