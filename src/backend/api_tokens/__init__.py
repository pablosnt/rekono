"""API token management package for Rekono.

This package provides secure API token management for user authentication.
It includes models for token creation, storage, and validation with security
features like unique key generation, expiration handling, and proper hashing.

Key Features:
    - Secure token generation with collision detection
    - Expiration date validation and enforcement
    - User-scoped token management
    - REST API endpoints for token lifecycle management

Security:
    - Tokens are hashed before database storage
    - Plain text tokens are only shown once during creation
    - User isolation prevents cross-user token access
"""
