"""Telegram Bot platform integration for Rekono.

Provides two-way Telegram integration. Rekono sends outbound notifications about
executions, alerts, and findings through the Telegram Bot API, and also exposes an
interactive bot that lets linked users manage targets, tasks, and tools through
chat commands.

Bot Capabilities:
    - Target, task, tool, and process configuration through chat commands
    - Role-based command gating that distinguishes Reader accounts from Auditor and Admin accounts
    - Account linking through a One-Time Password issued by the bot's /start command and
      redeemed through the telegram/link REST endpoint, not in the chat itself

Notification Capabilities:
    - Execution, alert, and finding notifications delivered as Telegram messages
    - Automatic splitting of long reports across multiple messages

Security:
    - Encrypted Bot API token storage
    - OTP-based account linking with expiration handling
    - User isolation, each Telegram chat can be linked to at most one Rekono account
"""
