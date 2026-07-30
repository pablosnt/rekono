"""Process management module for Rekono.

This module provides management of security testing processes and workflows
within the Rekono platform. It handles the creation and configuration of
multi-step security assessment processes, reusable sets of tool configurations
that are chained together and executed as complete vulnerability assessment
and penetration testing workflows.

Key Features:
    - Process creation and management with step-by-step tool configuration
    - Community-driven process sharing through a like system and tagging
    - Wordlist compatibility detection for content discovery tools
    - REST API endpoints for process and step lifecycle management
    - Fixture-based recreation that refreshes default processes while
      preserving user-created processes and their steps

Process Architecture:
    A process is a named collection of steps, and each step references the
    tool configuration to run. Steps carry no explicit order or dependency of
    their own. When a process is executed, the task engine resolves the run
    order from each step's tool stage and chains steps automatically whenever
    one step's output type matches another step's input type.

Security:
    - User-based ownership and access control for process management
    - Input validation and sanitization for process names and descriptions
    - Django model permissions combined with ownership checks for process
      and step access
"""
