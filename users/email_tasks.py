# email_tasks.py

import threading
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMessage
import datetime



def send_email(subject, message, from_email, recipient_list, html_message=None):
    email = EmailMessage(
        subject,
        message,
        from_email,
        recipient_list
    )
    if html_message:
        email.content_subtype = "html"  # Set the content type to HTML
        email.body = html_message
    email.send(fail_silently=False)

def send_welcome_email(user_email, user_name):
    subject = 'Welcome to Our Service'
    message = render_to_string('emails/welcome.html', {
        'user': user_name,
        'message': 'Thank you for registering.'
    })
    thread = threading.Thread(target=send_email, args=(subject, message, 'your_email@example.com', [user_email]))
    thread.start()

# Similarly, define functions for other emails
def send_login_email(user_email, user_name):
    subject = 'Welcome Back'
    message = render_to_string('emails/welcome_back.html', {
        'user': user_name,
        'message': 'Welcome back! We missed you.'
    })
    thread = threading.Thread(target=send_email, args=(subject, message, 'your_email@example.com', [user_email]))
    thread.start()

def send_logout_email(user_email, user_name):
    subject = 'You Logged Out'
    message = render_to_string('emails/logout.html', {
        'user': user_name,
        'message': 'You have successfully logged out.'
    })
    thread = threading.Thread(target=send_email, args=(subject, message, 'your_email@example.com', [user_email]))
    thread.start()

def send_password_reset_email(user_email, user_name):
    subject = 'Password Reset Successful'
    message = render_to_string('emails/password_reset.html', {
        'user': user_name,
        'message': 'Your password has been reset successfully.'
    })
    thread = threading.Thread(target=send_email, args=(subject, message, 'your_email@example.com', [user_email]))
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