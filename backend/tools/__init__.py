"""Security tools management module for Rekono.

This module defines the security testing tools that Rekono can run, their stage-based
configurations, and the command-line arguments each configuration accepts, mapped to
the input types they consume and the output types they produce. It also provides the
executor and parser frameworks, in the executors/ and parsers/ subpackages, that turn
those definitions into actual tool executions and turn tool output back into findings.

Key Features:
    - Tool model tracking installation status and detected version, with dynamic
      resolution of the tool-specific executor and parser classes based on its name
    - Configuration model defining stage-based command templates, a default
      configuration per tool, and deprecation that hides a configuration from new
      tasks and processes while keeping it resolvable for existing executions
    - Argument and Input models mapping configuration arguments to input types, with
      filtering, ordering, and multiplicity support for automated parameter generation
    - Output model declaring the input types a configuration produces, enabling one
      tool's output to feed another tool as input within a workflow
    - Intensity model defining per-tool intensity levels, from SNEAKY to INSANE, each
      mapped to its own command-line argument
    - REST API endpoints for tools and configurations, both read-only since tools and
      configurations are managed through fixtures, with filtering, search, and, for
      tools, like/unlike support
    - Fixture-based seeding on every migration: Tool and Configuration records are
      preserved to stay consistent with existing Tasks and Processes, while Intensity,
      Argument, Input, and Output are recreated so maintainers can reorder them freely
    - Automatic refresh of tool installation status and version after every migration

Architecture:
    executors/ contains BaseExecutor and the tool-specific executor classes that build
    command arguments from the available inputs and configuration, set up the
    execution environment, and run and track the tool subprocess. parsers/ contains
    BaseParser and the tool-specific parser classes that read a tool's output, in
    JSON, XML, or plain text, and turn it into Finding records.

Security:
    - A tool that is not installed on the system is skipped rather than executed
    - Environment variables passed to a tool subprocess are validated against a
      sensitive-value pattern before execution
    - XML tool output is parsed with defusedxml to prevent XXE attacks
    - REST API access to tools and configurations is gated by standard Django model
      permissions
"""
