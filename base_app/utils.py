from django.conf import settings
from django.core.mail import send_mail

def send_email_notification(subject, message, recipient_list):
    """
    Send general email notification
    """
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,  # From email
        recipient_list,  # To email list
        fail_silently=False,
    )
    return True 