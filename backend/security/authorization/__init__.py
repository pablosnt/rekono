"""Authorization and permission management module for Rekono.

This module implements role-based access control (RBAC) for the Rekono platform,
combining Django's group-based model permissions with custom Django REST Framework
permission classes. The `roles` submodule defines the role hierarchy and the
per-model permission mapping used to build the Django auth groups, while the
`permissions` submodule provides the permission classes that ViewSets combine to
enforce role-based, project-membership, and ownership checks.

Key Features:
    - Role hierarchy with a per-model view/add/change/delete permission mapping,
      assigned to Django auth groups automatically after migrations
    - RekonoModelPermission, extending Django's model permissions with explicit
      view permission enforcement for GET and HEAD requests
    - Role gates (IsAdmin, IsAuditor) and an anonymous-only gate
      (IsNotAuthenticated) for endpoints restricted by role rather than by model
      permission
    - Project membership enforcement (ProjectMemberPermission) for multi-tenant
      isolation of project-scoped resources
    - Ownership-based access control (OwnerPermission) restricting modification of
      personal resources to their owner, with a configurable admin override

Role Hierarchy:
    - Admin: full system access, including user management, project administration,
      and every platform integration and setting
    - Auditor: full access to run security testing and manage findings, without
      user or system administration privileges
    - Reader: view access to most security data, plus the ability to manage its
      own API tokens, notes, alerts, reports, and Telegram chat integration
"""
