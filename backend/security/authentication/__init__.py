"""Authentication module for Rekono security framework.

Provides authentication services for the Rekono platform, including API token
authentication, cookie-aware JWT authentication, and multi-factor authentication
built on TOTP with an email one-time password fallback. Includes the Django REST
Framework views and serializers that implement the login, MFA, refresh and logout
API endpoints.

Key Features:
    - API token authentication with cryptographic hashing and expiration checks
    - Cookie-aware JWT authentication that falls back to the Authorization header
    - TOTP-based multi-factor authentication with an email OTP fallback
    - Temporary, blacklistable MFA tokens scoped to MFA completion endpoints only

Integration:
    - Django REST Framework authentication backends and OpenAPI schema extensions
    - Email notifications for login events and MFA one-time passwords
"""
