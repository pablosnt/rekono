"""Alerts module for Rekono.

This module provides comprehensive alerting system for security teams to receive
real-time notifications about security findings. The system supports multiple
alert modes and filtering capabilities to reduce noise and focus on relevant threats.

Key Features:
    - Configurable alert rules with multiple trigger modes (NEW, FILTER, MONITOR)
    - Project-level alerting with fine-grained subscriber management
    - Automated background monitoring for trending vulnerabilities
    - REST API endpoints for alert lifecycle management
    - Background job processing with self-scheduling capabilities

Security:
    - Project-level access control and permission enforcement
    - Input validation and injection prevention for alert values
    - Secure subscription management with user isolation
    - Integration with external threat intelligence platforms
"""
