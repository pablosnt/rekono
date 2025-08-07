"""Project management module for Rekono.

This module provides comprehensive project management functionality for organizing
and controlling security testing engagements. It handles project lifecycle management,
team collaboration features, and integration with external vulnerability management
platforms for structured security testing workflows.

Key Features:
    - Complete project lifecycle management with team collaboration capabilities
    - Multi-user project workspace with role-based access control and member management
    - Tagging system for project organization and categorization
    - Automated alert configuration for trending CVE monitoring
    - Integration with DefectDojo for vulnerability management and reporting
    - Project-scoped access control for all security testing activities

Architecture:
    Projects serve as the central organizing unit for all security testing activities
    in Rekono. Each project contains targets, executions, findings, and team members
    with proper access control enforcement across all related resources. The project
    model provides the foundation for multi-tenant security testing operations.

Security:
    - Project-level access control enforcement across all related resources
    - Member-based authorization with owner privileges and team collaboration
    - Secure project creation with automatic owner membership assignment
    - Integration with external platforms using authenticated sessions
    - Automated security alerting with subscription management for team members
"""