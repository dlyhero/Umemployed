# email_tasks.py

import threading
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMessage
import datetime
from django.core.mail import EmailMultiAlternatives


def send_email(subject, plain_message, from_email, recipient_list, html_message=None):
    email = EmailMultiAlternatives(
        subject=subject,
        body=plain_message,  # The plain text content
        from_email=from_email,
        to=recipient_list
    )
    if html_message:
        email.attach_alternative(html_message, "text/html")  # Attach the HTML version
    email.send(fail_silently=False)

def send_welcome_email(user_email, user_name):
    subject = 'Welcome to Our Service'
    plain_message = f"Hello {user_name},\n\nThank you for registering."
    html_message = render_to_string('emails/welcome.html', {
        'user': user_name,
        'message': 'Thank you for registering.'
    })
    thread = threading.Thread(target=send_email, args=(subject, plain_message, 'your_email@example.com', [user_email], html_message))
    thread.start()

# Similarly, define functions for other emails
def send_login_email(user_email, user_name):
    subject = 'Welcome Back to UmEmployed'
    plain_message = f"Hello {user_name},\n\nWelcome back to UmEmployed."
    html_message = render_to_string('emails/welcome_back.html', {
        'user': user_name
    })
    thread = threading.Thread(target=send_email, args=(subject, plain_message, 'billleynyuy@gmail.com', [user_email], html_message))
    thread.start()

def send_logout_email(user_email, user_name):
    subject = 'See You Soon at UmEmployed!'
    plain_message = f"Goodbye {user_name},\n\nSee you soon at UmEmployed!"
    html_message = render_to_string('emails/logout.html', {
        'user': user_name
    })
    thread = threading.Thread(target=send_email, args=(subject, plain_message, 'billleynyuy@gmail.com', [user_email], html_message))
    thread.start()

def send_password_reset_email(user_email, user_name):
    subject = 'Password Reset Successful'
    plain_message = f"Hello {user_name},\n\nYour password has been reset successfully."
    html_message = render_to_string('emails/password_reset.html', {
        'user': user_name,
        'message': 'Your password has been reset successfully.'
    })
    thread = threading.Thread(target=send_email, args=(subject, plain_message, 'billleynyuy@gmail.com', [user_email], html_message))
    thread.start()

    
    
def send_new_job_email(user_email, user_name, job_title, job_link, job_description, company):
    subject = 'New Job Posted: {}'.format(job_title)
    html_message = render_to_string('emails/new_job.html', {
        'user': user_name,
        'company':company,
        'job_title': job_title,
        'job_link': job_link,
        'job_description': job_description,
        'current_year': datetime.datetime.now().year,
    })
    thread = threading.Thread(target=send_email, args=(subject, '', settings.DEFAULT_FROM_EMAIL, [user_email], html_message))
    thread.start()