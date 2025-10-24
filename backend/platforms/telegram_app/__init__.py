"""Telegram Bot platform integration for Rekono.

This module provides comprehensive Telegram Bot integration for security teams to
interact with Rekono's security testing platform through conversational interfaces.
The system supports authenticated bot interactions, user account linking, and
secure command execution for security testing workflows.

Bot Capabilities:
    - Target management through chat commands
    - Security tool configuration and execution
    - Reporting of found vulnerabilities
    - Real-time notifications and alerts through Telegram channels

Security:
    - Encrypted API token storage for bot authentication
    - User isolation with chat-based access control
    - OTP-based account linking with expiration handling
    - Role-based command authorization and validation
    - Secure integration with Rekono's authentication system
"""
