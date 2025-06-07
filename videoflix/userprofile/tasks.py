
from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from .models import CustomUser
from celery import shared_task
from django.conf import settings
url = settings.FRONTEND_BASEURL

@shared_task
def send_verification_email_to_user(code, user_id):
    """
    Asynchronous Celery task to send a verification email to a user.

    Parameters:
    - code (str):  
    The verification code to include in the email.

    - user_id (int or UUID):  
    The ID of the user to whom the email will be sent.

    Functionality:
    - Retrieves the user instance by `user_id`.
    - Prepares an email context with username, user ID, verification code, and a URL (assumed to be defined elsewhere).
    - Renders the HTML email content from the template 'emails/verify_email.html'.
    - Constructs and sends an HTML email with the subject "Confirm your email" from the configured sender address.
    - Sends the email asynchronously via Celery, enabling non-blocking email dispatch.

    Notes:
    - Relies on Django settings for the email sender address (`EMAIL_FROM`).
    - Assumes the variable `url` is defined in the task's scope or elsewhere (may need to be passed explicitly).
    - Designed to improve user experience by handling email sending in the background.
    """

    sender = settings.EMAIL_FROM
    user = CustomUser.objects.get(id=user_id)
    context = {'username': user.username, 'user_id': user_id, 'code':code, 'url':url}
    html_content = render_to_string('emails/verify_email.html', context=context)
    email = EmailMessage(
        subject="Confirm your email", 
        body=html_content, 
        from_email=sender,
        to=[user.email], 
    )
    email.content_subtype = "html" 
    email.send()

@shared_task
def send_password_reset_email_to_user(code, user_id):
    """
    Asynchronous Celery task to send a password reset email to a user.

    Parameters:
    - code (str):  
    The password reset code to include in the email.

    - user_id (int or UUID):  
    The ID of the user to whom the reset email will be sent.

    Functionality:
    - Fetches the user instance using the given `user_id`.
    - Constructs an email context containing the user ID, reset code, and a URL (assumed to be defined elsewhere).
    - Renders the HTML content of the email using the 'emails/reset_password_email.html' template.
    - Creates an HTML email with the subject "Reset your Password", from the configured sender address.
    - Sends the email asynchronously via Celery for non-blocking operation.

    Notes:
    - Uses the `EMAIL_FROM` setting for the sender email address.
    - Assumes the variable `url` is available in scope or should be passed as an argument.
    - Improves user experience by delegating email sending to background tasks.
    """

    sender = settings.EMAIL_FROM
    user = CustomUser.objects.get(id=user_id)
    context = {'user_id': user_id, 'code':code, 'url':url}
    html_content = render_to_string('emails/reset_password_email.html', context=context)
    email = EmailMessage(
        subject="Reset your Password", 
        body=html_content, 
        from_email=sender,
        to=[user.email], 
    )
    email.content_subtype = "html" 
    email.send()

