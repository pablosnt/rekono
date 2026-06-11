"""Email notification platform for Rekono.

This module provides comprehensive email notification capabilities for the Rekono
security testing platform through SMTP integration. It enables automated email
notifications for security findings, alerts, user management events, and system
notifications, ensuring that security teams stay informed of critical discoveries
and platform activities in real-time.

Key Features:
    - SMTP configuration management with encrypted credential storage
    - HTML email templates authored in React (email-templates/) and built to
      platforms/email/templates/ via react-email's export pipeline
    - Real-time notifications for security findings and alerts
    - User lifecycle notifications (invitations, password resets, MFA)
    - Background email processing for optimal performance
    - Connection testing and availability validation

Security:
    - SMTP credentials encrypted before database storage
    - Secure TLS/SSL connection support with certificate validation
    - Input validation and injection prevention for email content
    - Integration with user permission system for notification targeting
"""
