"""Security tools management module for Rekono.

This module provides comprehensive management of security testing tools and their
configurations within the Rekono platform. It handles tool discovery, installation
status tracking, configuration management, and execution parameters for automated
security testing workflows integrated with various open-source security tools.

Tool Architecture:
    The tools system uses a modular approach where each security tool has associated
    parser and executor classes for handling tool-specific execution logic and output
    processing. Tools are configured with input/output types, arguments, and stages
    that determine their role in security testing workflows.

Security:
    - Project-level access control for tool configurations and executions
    - Secure handling of tool arguments and execution parameters
    - Installation validation to prevent execution of unavailable tools
    - Integration with external tools using validated command execution
"""
