"""Telegram Bot mixin for target port creation and management workflows.

Provides target port creation functionality for conversations that require
port specification including validation, creation, and summary display.
"""

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from platforms.telegram_app.bot.commands import Cancel
from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.bot.mixins.framework import BaseMixin
from target_ports.serializers import TargetPortSerializer


class TargetPortMixin(BaseMixin):
    """Mixin providing target port creation functionality.

    Enables conversations to create new target ports with validation
    and error handling for security testing workflows.
    """

    async def ask_for_new_target_port(self, update: Update, context: CallbackContext) -> int:
        """Prompt user to input a new target port number.

        Requests user to provide port number for target port creation.

        Args:
            update (Update): The Telegram update containing user interaction.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int: Next conversation state for port input processing.
        """
        self.validate_update(update)
        return await self.go_to_next_state(
            update,
            context,
            await self.ask_for_new_attribute(
                update, "target port", "port", self.get_next_state(self.ask_for_new_target_port)
            ),
        )

    async def create_target_port(self, update: Update, context: CallbackContext) -> int | None:
        """Create target port from user input with validation.

        Processes user input to create a target port, validates port number format,
        and handles cancellation commands with proper error messaging.

        Args:
            update (Update): The Telegram update containing port number input.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int | None: Next conversation state after port creation or error handling.
        """
        self.validate_update(update)
        if not update.effective_message or not update.effective_message.text:
            return ConversationHandler.END
        if update.effective_message.text.lower() == "/cancel":
            return await Cancel().execute_command(update, context)
        try:
            port = int(update.effective_message.text)
        except ValueError:
            await self.reply(update, "Port must be a valid number")
            return await self.go_to_next_state(update, context, self.get_previous_state(self.create_target_port))
        target = self.get_context_value(context, Context.TARGET)
        if not target:
            await self.reply(update, "No target selected")
            return ConversationHandler.END
        next_state, instance = await self.create(
            update,
            context,
            TargetPortSerializer,
            {"target": target.id, "port": port, "path": None},
            self.get_previous_state(self.create_target_port),
            self.get_next_state(self.create_target_port),
        )
        if instance:
            self.add_context_value(context, Context.TARGET_PORT, instance)
        return await self.go_to_next_state(update, context, next_state, invoke_next_state=instance is None)

    async def reply_summary(self, update: Update, context: Context) -> int:
        """Display target port creation summary to user.

        Shows confirmation message with created target port details and
        cleans up conversation context.

        Args:
            update (Update): The Telegram update containing user interaction.
            context (Context): The conversation context containing port data.

        Returns:
            int: Next conversation state after summary display.
        """
        self.validate_update(update)
        target_port = self.get_context_value(context, Context.TARGET_PORT)
        if target_port:
            await self.reply(
                update,
                f"New target port *{target_port.port}* has been created in target *{self.escape(target_port.target.target)}*",
            )
        self.remove_all_context_values(context)
        return await self.go_to_next_state(update, context, self.get_next_state(self.reply_summary))
