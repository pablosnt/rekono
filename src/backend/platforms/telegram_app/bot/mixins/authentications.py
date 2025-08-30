"""Telegram Bot mixin for authentication configuration workflows.

Provides authentication type selection and authentication credential creation
functionality for conversations that require authentication setup for targets.
"""

from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from authentications.enums import AuthenticationType
from authentications.serializers import AuthenticationSerializer
from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.bot.mixins.framework import BaseMixin


class AuthenticationMixin(BaseMixin):
    """Mixin providing authentication configuration functionality.

    Enables conversations to configure authentication credentials for targets
    including authentication type selection and credential creation workflows.

    Attributes:
        no_authentication (str): Option value for no authentication required.
        new_port_command (str): Command name that allows "no authentication" option.
    """

    no_authentication = "None"
    new_port_command = "newport"

    async def ask_for_authentication_type(self, update: Update, context: CallbackContext) -> int:
        """Display authentication type selection options.

        Shows available authentication types with optional "None" choice for
        newport command workflows.

        Args:
            update (Update): The Telegram update containing user interaction.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int: Next conversation state for authentication type selection.
        """
        self.validate_update(update)
        values = AuthenticationType.values
        current_command = self.get_context_value(context, Context.COMMAND)
        if current_command and current_command.lower() == self.new_port_command:
            values.append(self.no_authentication)
        return await self.go_to_next_state(
            update,
            context,
            await self.ask_values(
                update,
                values,
                3,
                "Choose authentication type",
                self.get_next_state(self.ask_for_authentication_type),
            ),
        )

    async def save_authentication_type(self, update: Update, context: CallbackContext) -> int:
        """Save selected authentication type to conversation context.

        Processes authentication type selection and handles special case for
        "None" authentication, skipping credential creation.

        Args:
            update (Update): The Telegram update containing callback selection.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int: Next conversation state based on authentication type.
        """
        self.validate_update(update)
        if (
            update.callback_query
            and update.callback_query.data
            and update.callback_query.data == self.no_authentication
        ):
            return await self.go_to_next_state(update, context, self.get_next_state(self.create_authentication))
        else:
            return await self.go_to_next_state(
                update,
                context,
                await self.save_value(
                    update,
                    context,
                    Context.AUTHENTICATION_TYPE,
                    "AuthenticationType",
                    self.get_next_state(self.save_authentication_type),
                ),
            )

    async def ask_for_new_authentication(self, update: Update, context: CallbackContext) -> int:
        """Prompt user to input authentication credentials.

        Requests user to provide authentication credentials in 'name - secret' format.

        Args:
            update (Update): The Telegram update containing user interaction.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int: Next conversation state for credential input processing.
        """
        self.validate_update(update)
        return await self.go_to_next_state(
            update,
            context,
            await self.ask_for_new_attribute(
                update, "authentication", "'name \- secret'", self.get_next_state(self.ask_for_new_authentication)
            ),
        )

    async def create_authentication(self, update: Update, context: CallbackContext) -> int:
        """Create authentication credentials from user input.

        Parses user input in 'name - secret' format and creates authentication
        credentials for the selected target port with validation and error handling.

        Args:
            update (Update): The Telegram update containing credential input.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int: Next conversation state after authentication creation.
        """
        self.validate_update(update)
        if not update.effective_message or not update.effective_message.text:
            return ConversationHandler.END
        name = update.effective_message.text
        secret = None
        if name and " - " in name:
            name, secret = name.split(" - ", 1)
        target_port = self.get_context_value(context, Context.TARGET_PORT)
        if not target_port:
            self.reply(update, "No target port selected")
            return ConversationHandler.END
        next_state, instance = await self.create(
            update,
            context,
            AuthenticationSerializer,
            {
                "name": name,
                "secret": secret,
                "type": self.get_context_value(context, Context.AUTHENTICATION_TYPE),
                "target_port": target_port.id,
            },
            self.get_previous_state(self.create_authentication),
            self.get_next_state(self.create_authentication),
        )
        if instance:
            self.add_context_value(context, Context.AUTHENTICATION, instance)
        return await self.go_to_next_state(update, context, next_state)
