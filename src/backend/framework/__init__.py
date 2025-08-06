"""Framework module for Rekono.

This module provides the core framework infrastructure for Rekono's security testing
platform. It includes base classes, utilities, and common functionality used across
all other modules to ensure consistent behavior, security, and maintainability.

Key Features:
    - Base model classes with project-level access control and encryption support
    - Standardized Django REST framework ViewSets and serializers with security controls
    - Advanced filtering and pagination capabilities for API endpoints
    - Logging infrastructure with request tracking and user identification
    - Integration platforms for external security tools and services
    - Background job processing with Redis Queue (RQ) integration
    - Custom field types and validation for security-focused applications

Architecture:
    The framework follows a modular design with base classes that provide common
    functionality while allowing specialization in derived modules. All components
    integrate seamlessly with Django's ORM and Django REST framework to provide
    a secure, scalable foundation for security testing operations.

Security:
    - Project-level access control enforcement across all model operations
    - Automatic encryption for sensitive data fields using AES encryption
    - Comprehensive input validation and injection prevention
    - Secure logging with user tracking and audit trails
    - Integration with external platforms using authenticated sessions
    - Background job processing with secure parameter handling
"""