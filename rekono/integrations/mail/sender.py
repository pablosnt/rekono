from typing import Any
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.conf import settings


def send_invitation_to_new_user(user: Any, domain: str) -> None:
    template = get_template('invitation_to_new_user.html')
    context = {'registration_url': f'http://{domain}/any/path?token={user.otp}'}
    content = template.render(context)
    subject = 'Welcome to Rekono'
    message = EmailMultiAlternatives(subject, '', settings.EMAIL_HOST_USER, [user.email])
    message.attach_alternative(content, 'text/html')
    message.send()
