"""Security module for Rekono.

This module provides comprehensive security infrastructure for the Rekono platform,
including authentication, authorization, cryptography, file handling, and validation
components. It ensures secure operations across all platform components with
defense-in-depth security controls and enterprise-grade security features.

Key Features:
    - Multi-factor authentication with TOTP and backup codes
    - Role-based access control with project-level permissions
    - AES encryption for sensitive data storage and transmission
    - Secure file upload validation with MIME type checking
    - Input validation with injection attack prevention
    - Middleware for security headers and request filtering
    - Management commands for encryption key lifecycle management

Integration:
    - Seamless integration with Django authentication framework
    - Django REST Framework authentication and permissions
    - Logging and monitoring for security events and audit trails
"""
