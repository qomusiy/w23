from django.core.mail import send_mail
from project import settings


def send_to_mail(request, email, message):
    message = f"tasdiqlash kodi: {message}"
    subject = "tasdiqlash kodi"
    address = email
    send_mail(subject, settings.EMAIL_HOST_USER, [address])
