
import smtplib
from django.conf import settings
from django.core.mail import send_mail, get_connection
from django.core.mail import EmailMessage

from django.template import Context
from django.template.loader import render_to_string

from .models import CustomUser
from celery import shared_task


@shared_task
def send_email_to_user(code, user_id):
    sender = settings.EMAIL_FROM
    user = CustomUser.objects.get(id=user_id)
    context = {'username': user.username, 'user_id': user_id, 'code':code}
    html_content = render_to_string('emails/email.html', context=context)
    email = EmailMessage(
        subject="Dein Bestätigungslink",  # Betreff der E-Mail
        body=html_content,  # HTML-Inhalt der E-Mail
        from_email=sender,
        to=[user.email],  # Empfänger-Adresse
    )
    email.content_subtype = "html"  # Setzt den Inhaltstyp auf HTML
    email.send()