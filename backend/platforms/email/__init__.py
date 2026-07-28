"""Email notification platform for Rekono.

This module provides outbound email notification capabilities for the Rekono
security testing platform through SMTP integration. Rekono sends mail, it does not
fetch data from mailboxes. It covers execution and alert notifications, user
lifecycle notifications (invitations, password resets, MFA), and report-ready
notifications.

Key Features:
    - SMTP configuration management with encrypted credential storage
    - HTML email templates authored in React (email-templates/) and built to
      platforms/email/templates/ via react-email's export pipeline
    - Execution and alert notifications for discovered security findings
    - User lifecycle notifications (invitations, password resets, MFA)
    - Background email processing for user lifecycle notifications
    - Connection testing and availability validation, skipped while CONFIG.testing

Security:
    - SMTP credentials encrypted before database storage
    - Secure TLS/SSL connection support with certificate validation
    - Per-user notification preferences control who receives execution and
      report emails
"""
