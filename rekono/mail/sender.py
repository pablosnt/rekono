from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

from rekono.settings import EMAIL_HOST_USER, REKONO_ADDRESS


def send_html_message(to_address: str, meta: dict, parameters: dict) -> None:
    parameters['rekono_address'] = REKONO_ADDRESS
    message = EmailMultiAlternatives(meta.pop('subject'), '', EMAIL_HOST_USER, [to_address])
    template = get_template(meta.pop('template'))
    content = template.render(parameters)
    message.attach_alternative(content, 'text/html')
    message.send()
