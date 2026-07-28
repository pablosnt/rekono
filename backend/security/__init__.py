"""Security module for Rekono.

This module provides the security infrastructure for the Rekono platform,
including authentication, authorization, cryptography, file handling, CSP
violation reporting, and input validation. It applies defense-in-depth
controls across the platform, from HTTP-level protections in the
request/response middleware down to field-level encryption of stored secrets.

Key Features:
    - Multi-factor authentication via TOTP with an email OTP fallback
    - Role-based access control with project-level permissions
    - Fernet encryption for sensitive data at rest, plus SHA-512 hashing
    - Secure file upload validation with MIME type checking
    - Input and pentest-target validation with injection attack prevention
    - Security headers, CSP enforcement, and CORS handling via HTTP middleware
    - CSP violation reporting endpoints for browser-submitted reports
    - Management commands for encryption key lifecycle management

Integration:
    - Django REST Framework authentication backends and permission classes
    - Logging and monitoring for security events and audit trails
"""
