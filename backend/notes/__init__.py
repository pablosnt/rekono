"""Notes and documentation management module for Rekono.

This module provides comprehensive note-taking and documentation capabilities
for security teams to capture, organize, and share insights throughout security
assessments. The notes system supports contextual note attachment to various
entities including projects, targets, findings, and executions with collaborative
features like forking, tagging, and like functionality.

Key Features:
    - Contextual note attachment to any entity in the security assessment workflow
    - Collaborative note sharing with public/private visibility controls
    - Note forking system for knowledge base development and sharing
    - Tagging system for note organization and categorization
    - Like/unlike functionality for community-driven content curation
    - Full-text search capabilities across note titles and content
    - User ownership and permission management with access controls

Workflow Integration:
    Notes can be attached to various entities throughout the security assessment
    lifecycle, enabling teams to document insights, observations, and analysis
    directly within context. The system supports both individual and collaborative
    workflows with sharing and forking capabilities.

Security:
    - Project-level access control and permission enforcement
    - User-based ownership and privacy controls for sensitive documentation
    - Input validation and sanitization for all note content
"""
