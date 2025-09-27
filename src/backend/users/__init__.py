"""User management module for Rekono.

This module provides comprehensive user account management and authentication
functionalities for the Rekono security testing platform. It handles the complete
lifecycle of user accounts from invitation and registration through profile management,
authentication, and role-based access control with advanced security features.

Key Features:
    - User invitation and account creation workflow with email verification
    - Role-based access control with granular permission management
    - Multi-factor authentication (MFA) with TOTP authenticator app support
    - One-time password (OTP) system for secure operations and password resets
    - Comprehensive user profile management with notification preferences
    - Advanced authentication with JWT tokens and API key support
    - Password management with secure validation and reset capabilities
    - Integration with external notification systems (Email, Telegram)

Authentication Flow:
    - Users are invited by administrators and receive email invitations
    - Account creation requires valid OTP from invitation email
    - Authentication supports both password-based and MFA verification
    - Secure session management with JWT token blacklisting
    - API token generation for programmatic access

Security:
    - Project-level access control and permission enforcement
    - Secure password hashing with Django's authentication system
    - Encrypted storage of MFA secrets using AES encryption
    - Input validation and injection prevention for all user data
    - Comprehensive audit logging for security-sensitive operations
    - Protection against user enumeration attacks
    - Secure token management with automatic invalidation
"""
