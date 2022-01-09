from typing import Any

from mail.sender import send_html_message


def send_invitation_to_new_user(user: Any) -> None:
    metadata = {
        'template': 'invitation_to_new_user.html',
        'subject': 'Welcome to Rekono',
    }
    send_html_message(user.email, metadata, {'otp': user.otp})


def send_password_reset(user: Any) -> None:
    metadata = {
        'subject': 'Reset your Rekono password',
        'template': 'reset_password.html',
    }
    send_html_message(user.email, metadata, {'otp': user.otp})
