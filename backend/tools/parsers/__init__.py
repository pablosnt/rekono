"""Tool output parsers package for Rekono.

This package provides parser classes for extracting security findings from
tool execution outputs. Each parser is responsible for processing tool-specific
output formats and converting them into standardized finding objects for
storage and analysis within the Rekono platform.

Key Features:
    - Tool-specific parser implementations for output processing
    - Standardized finding extraction and creation workflow
    - Support for multiple output formats (JSON, XML, text)
    - Relationship management between findings and executions
    - Base parser class with common functionality for all parsers

Architecture:
    Parsers follow a plugin architecture where each tool has a dedicated parser
    class that inherits from BaseParser. The system automatically selects the
    appropriate parser based on the tool name, falling back to BaseParser for
    tools without specific implementations.

Security:
    - Secure XML parsing using defusedxml to prevent XXE attacks
    - Duplicate finding detection and automatic relationship linking during finding creation
    - Proper handling of sensitive information in tool outputs
    - Parsing failures are caught and logged rather than propagated, so a broken
      parser never crashes the wider execution pipeline
"""
