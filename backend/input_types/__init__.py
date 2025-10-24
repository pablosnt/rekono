"""Input types module for Rekono.

This module provides comprehensive management of input type definitions used
throughout the Rekono security testing platform. It enables dynamic discovery
and validation of input data categories for security tools, supporting flexible
tool argument mapping and relationship analysis between different finding types.

Key Features:
    - Dynamic input type discovery with Django model integration
    - Configurable primary and fallback model references for data handling
    - Relationship calculation between input types for tool chaining
    - Type-safe input validation and model mapping
    - REST API endpoints for input type configuration management
    - Integration with security tool argument systems

Architecture:
    The input types system uses a mapping-based approach where each input type
    (OSINT, Host, Port, etc.) can be associated with specific Django models.
    This design enables flexible tool integration while maintaining type safety
    and supporting complex tool workflows with input dependencies.
"""
