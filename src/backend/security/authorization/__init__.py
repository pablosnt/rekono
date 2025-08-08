"""Authorization and permission management for Rekono security framework.

Provides role-based access control (RBAC) and permission management for the Rekono
platform. This module implements fine-grained authorization controls including
role definitions, permission mappings, and custom permission classes for Django
REST Framework integration.

Role Hierarchy:
    - Admin: Full system access including user and system management
    - Auditor: Read-write access to security data and findings
    - Reader: Read-only access to security data and reports

Permission Model:
    - View permissions: Control read access to resources
    - Add permissions: Control resource creation capabilities
    - Change permissions: Control resource modification rights
    - Delete permissions: Control resource deletion authority
"""
