
import smtplib
from django.conf import settings
from django.core.mail import send_mail, get_connection
from django.core.mail import EmailMessage

from django.template import Context
from django.template.loader import render_to_string

from .models import CustomUser
from celery import shared_task
from django.conf import settings

url = settings.FRONTEND_BASEURL

@shared_task
def send_verification_email_to_user(code, user_id):
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