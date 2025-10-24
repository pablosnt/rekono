"""Authentication management module for Rekono.

This module provides functionality for managing authentication credentials used
in security testing and penetration testing workflows. It includes models for
storing various types of authentication data with encryption for sensitive
information and validation for input data.

Key Features:
    - Support for multiple authentication types (Basic, Bearer, Cookie, etc.)
    - Automatic encryption of sensitive credential data
    - Input validation with injection attack prevention
    - Project-scoped access control and authorization
    - REST API endpoints for credential lifecycle management

Security:
    - All sensitive data is encrypted before database storage
    - Credentials are never stored in plain text
    - Secure field handling with ProtectedSecretField implementation
    - Integration with security testing tools and frameworks
"""
