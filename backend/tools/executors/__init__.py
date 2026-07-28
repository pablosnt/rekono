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
    - Authentication secrets and tokens are masked with asterisks before the
      executed command is logged or persisted
    - Commands run as an argument list via subprocess without invoking a shell,
      so shell metacharacters in tool arguments are never interpreted
    - Environment variable assignments parsed from the command line are checked
      against a sensitive-variable pattern (PATH, LD_PRELOAD, etc.) and dropped,
      with a warning logged, instead of being applied to the subprocess
    - Tools that are not installed on the system are skipped instead of executed
"""
