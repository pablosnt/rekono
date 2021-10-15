from typing import Any
from integrations.mail.utils import send_html_message


metadata = {
    'invitation': {
        'template': 'invitation_to_new_user.html',
        'subject': 'Welcome to Rekono',
        # 'link': 'http://{domain}/any/path/?token={otp}'
    },
    'passwd_reset': {
        'subject': 'Reset your Rekono password',
        'template': 'reset_password.html',
        # 'link': 'http://{domain}/any/path/?token={otp}',
    }
}


def send_invitation_to_new_user(user: Any, domain: str) -> None:
    send_html_message(user.email, metadata.get('invitation'), {'domain': domain, 'otp': user.otp})


def send_password_reset(user: Any, domain: str) -> None:
    send_html_message(user.email, metadata.get('passwd_reset'), {'domain': domain, 'otp': user.otp})
