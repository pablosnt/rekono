from typing import Any, Dict, List

import django_rq
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django_rq import job
from findings.models import Finding

from rekono.settings import EMAIL_HOST_USER, REKONO_ADDRESS


@job('emails-queue')
def consumer(addresses: List[str], subject: str, template_name: str, data: Dict[str, Any]) -> None:
    '''Send HTML email message.

    Args:
        addresses (List[str]): Destinatary email addresses
        subject (str): Email subject
        template_name (str): HTML template to use
        data (Dict[str, Any]): Data to include in the HTML template
    '''
    template = get_template(template_name)                                      # Get HTML template
    data['rekono_address'] = REKONO_ADDRESS                                     # Include frontend address for links
    content = template.render(data)                                             # Render HTML template using data
    message = EmailMultiAlternatives(subject, '', EMAIL_HOST_USER, addresses)   # Create email message
    message.attach_alternative(content, 'text/html')                            # Add HTML content to email message
    message.send()                                                              # Send email message


def user_invitation(user: Any) -> None:
    '''Send email user invitation.

    Args:
        user (Any): User to invite to Rekono
    '''
    emails_queue = django_rq.get_queue('emails-queue')                          # Get emails queue
    emails_queue.enqueue(                                                       # Enqueue email notification
        consumer,
        addresses=[user.email],
        subject='Welcome to Rekono',
        template_name='user_invitation.html',
        data={'user': user}
    )


def user_password_reset(user: Any) -> None:
    '''Send email for reset password.

    Args:
        user (Any): User that requests the password reset
    '''
    emails_queue = django_rq.get_queue('emails-queue')                          # Get emails queue
    emails_queue.enqueue(                                                       # Enqueue email notification
        consumer,
        addresses=[user.email],
        subject='Reset Rekono password',
        template_name='user_password_reset.html',
        data={'user': user}
    )


def user_enable_account(user: Any) -> None:
    '''Send email for enable user account.

    Args:
        user (Any): Recently enabled user
    '''
    emails_queue = django_rq.get_queue('emails-queue')                          # Get emails queue
    emails_queue.enqueue(                                                       # Enqueue email notification
        consumer,
        addresses=[user.email],
        subject='Rekono user enabled',
        template_name='user_enable_account.html',
        data={'user': user}
    )


def execution_notifications(emails: List[str], execution: Any, findings: List[Finding]) -> None:
    '''Send email notifications with execution results.

    Args:
        emails (List[str]): Email address list to notify
        execution (Any): Completed execution
        findings (List[Finding]): Findings obtained during execution
    '''
    data = {                                                                    # Data to include in notification
        'execution': execution,
        'tool': execution.step.tool if execution.step else execution.task.tool,
        'configuration': execution.step.configuration if execution.step else execution.task.configuration
    }
    for finding in findings:                                                    # For each finding
        if finding.__class__.__name__.lower() not in data:
            data[finding.__class__.__name__.lower()] = []
        data[finding.__class__.__name__.lower()].append(finding)                # Add finding to the data
    # Send email notifications
    emails_queue = django_rq.get_queue('emails-queue')                          # Get emails queue
    emails_queue.enqueue(                                                       # Enqueue email notifications
        consumer,
        addresses=emails,
        subject=f'[Rekono] {data["tool"].name} execution completed',
        template_name='execution_notification.html',
        data=data
    )
