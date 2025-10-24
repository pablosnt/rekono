"""Process management module for Rekono.

This module provides comprehensive management of security testing processes and
workflows within the Rekono platform. It handles the creation, configuration,
and execution of multi-step security assessment processes that chain together
various security tools to perform complete vulnerability assessments and
penetration testing workflows.

Key Features:
    - Process creation and management with step-by-step tool configuration
    - Workflow orchestration for automated security testing pipelines
    - Tool chaining with dependency management for complex assessments
    - Community-driven process sharing with tagging and rating system
    - Wordlist compatibility detection for content discovery tools
    - REST API endpoints for process and step lifecycle management

Process Architecture:
    Processes consist of multiple sequential steps, where each step represents
    a configured security tool execution. The system supports tool chaining,
    dependency management, and conditional execution based on previous step
    results. This enables automated security testing workflows from initial
    reconnaissance through vulnerability exploitation.

Security:
    - User-based ownership and access control for process management
    - Input validation and sanitization for process configurations
    - Secure parameter handling for tool execution workflows
    - Integration with project-level permission enforcement
"""
