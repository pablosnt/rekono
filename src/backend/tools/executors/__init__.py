"""Tool executors package for Rekono.

This package provides executor classes for running security tools with proper
parameter generation, command construction, and execution management. Each
executor handles tool-specific logic for argument preparation, environment
setup, and execution control within the Rekono security testing platform.

Key Features:
    - Tool-specific executor implementations for command construction
    - Automated argument generation from available inputs and configurations
    - Environment variable management and execution directory control
    - Integration with authentication systems and credential management
    - Support for intensity levels and execution parameters
    - Base executor class with common functionality for all tools

Architecture:
    Executors follow a plugin architecture where each tool has a dedicated executor
    class that inherits from BaseExecutor. The system automatically selects the
    appropriate executor based on the tool name, falling back to BaseExecutor for
    tools without specific implementations.

Security:
    - Secure handling of authentication credentials and sensitive parameters
    - Command injection prevention through proper argument escaping
    - Controlled execution environments with appropriate permissions
    - Integration with encryption systems for credential management
"""