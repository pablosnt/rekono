"""Rekono security testing platform main package.

This package contains the core Django application configuration and infrastructure
for Rekono, a comprehensive penetration testing automation platform that combines
multiple security tools to complete comprehensive security assessments.

The platform provides a unified interface for orchestrating security testing
workflows, managing findings, and generating reports across diverse security
testing scenarios including network scanning, vulnerability assessment, and
exploitation automation.

Key Features:
    - Automated security testing workflow orchestration and execution management
    - Multi-tool integration with standardized output parsing and correlation
    - Project-based assessment organization with role-based access control
    - Real-time finding management with triage workflows and false positive handling
    - Comprehensive reporting with export capabilities and integration support
    - Background job processing with Redis Queue for scalable task execution
    - External platform integrations including DefectDojo, CVE databases, and notification systems

Architecture:
    Rekono follows a modular Django architecture with clear separation of concerns
    across functional domains. The platform uses Django REST Framework for API
    endpoints, Celery/RQ for background processing, and PostgreSQL for data persistence.
    Each module provides specialized functionality while integrating seamlessly through
    the framework's base classes and shared infrastructure components.

Security:
    - Project-level access control with membership-based authorization
    - Encrypted storage for sensitive data including credentials and tokens
    - Comprehensive input validation and injection prevention across all endpoints
    - Audit logging for all user actions and system operations
    - Secure integration with external platforms using authenticated sessions
    - Rate limiting and request throttling for API endpoint protection
"""