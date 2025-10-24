"""Task management module for Rekono.

This module provides comprehensive task orchestration and execution management for
security testing workflows. It handles the complete lifecycle of security tasks
from creation to completion, including scheduling, dependency management, tool
execution coordination, and progress tracking for automated security assessments.

Task Types:
    - Single Tool Tasks: Execute individual security tools with specific configurations
    - Process Tasks: Execute multi-step security processes with tool dependency management
    - Scheduled Tasks: Execute tasks at future dates with optional recurring schedules
    - Repeating Tasks: Periodically create tasks based on configured intervals

Security:
    - Project-level access control and permission enforcement
    - Secure parameter handling for tool execution
    - User ownership and authorization management
    - Safe cancellation and cleanup of running tasks
"""
