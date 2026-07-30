"""Telegram Bot mixin for target port creation and selection workflows.

Provides target port functionality for conversations that require port
specification, covering creation with validation and summary display, and
selection of an existing port to focus an execution on a single target port.
Every state here expects Context.TARGET to already be set by TargetMixin.
reply_summary is only used by the /newport conversation, which ends there;
other conversations leave Context.TARGET_PORT set (or unset for "all ports")
and move on to further mixins instead.
"""

from asgiref.sync import sync_to_async
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, ConversationHandler

from platforms.telegram_app.bot.commands import Cancel
from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.bot.mixins.framework import BaseMixin
from target_ports.models import TargetPort
from target_ports.serializers import TargetPortSerializer
from targets.models import Target


class TargetPortMixin(BaseMixin):
    """Mixin providing target port creation and selection functionality.

    Enables conversations to create new target ports and to select an existing
    target port to focus an execution on, with validation and error handling
    for security testing workflows.

    Attributes:
        all_target_ports (str): Label for the option that runs against the whole
                                target without linking the task to any target port.
    """

    all_target_ports = "🌐 All ports"

    @sync_to_async
    def _get_target_ports_keyboard_async(self, target: Target) -> list[InlineKeyboardButton]:
        """Generate keyboard buttons for the target ports of a target (async wrapper).

        Args:
            target (Target): The target whose ports should be listed.

        Returns:
            list[InlineKeyboardButton]: Buttons for the available target ports,
                                        showing the path when present.
        """
        return [
            InlineKeyboardButton(f"{tp.port} - {tp.path}" if tp.path else str(tp.port), callback_data=tp.id)
            for tp in TargetPort.objects.filter(target=target).order_by("port")
        ]

    async def ask_for_target_port(self, update: Update, context: CallbackContext) -> int:
        """Display target port selection options for the selected target.

        Shows one button per target port of the selected target plus an option to
        run against the whole target. When the target has no ports, the step is
        skipped silently and the conversation advances to the next state.

        Args:
            update (Update): The Telegram update containing user interaction.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int: Next conversation state after the prompt or when skipped.
        """
        self.validate_update(update)
        target = self.get_context_value(context, Context.TARGET)
        if not target:
            await self.reply(update, "No target selected")
            return ConversationHandler.END
        keyboard = await self._get_target_ports_keyboard_async(target)
        if not keyboard:
            return await self.go_to_next_state(update, context, self.get_next_state(self.save_target_port))
        keyboard.append(InlineKeyboardButton(self.all_target_ports, callback_data=self.all_target_ports))
        await self.reply(update, "Choose target port", reply_markup=InlineKeyboardMarkup([[item] for item in keyboard]))
        return await self.go_to_next_state(update, context, self.get_next_state(self.ask_for_target_port))

    async def save_target_port(self, update: Update, context: CallbackContext) -> int:
        """Save the selected target port to conversation context.

        Stores the selected target port in the conversation context. When the user
        chooses to run against the whole target, nothing is stored so the task is
        not linked to any target port.

        Args:
            update (Update): The Telegram update containing target port selection.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int: Next conversation state after target port selection.
        """
        self.validate_update(update)
        if update.callback_query and update.callback_query.data == self.all_target_ports:
            await update.callback_query.answer()
            return await self.go_to_next_state(update, context, self.get_next_state(self.save_target_port))
        return await self.go_to_next_state(
            update,
            context,
            await self.save(
                update, context, Context.TARGET_PORT, TargetPort, self.get_next_state(self.save_target_port)
            ),
        )

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
        # This state's MessageHandler(filters.TEXT, ...) matches "/cancel" as plain text too, so it
        # has to be redirected to the Cancel command manually before parsing it as a port number
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
