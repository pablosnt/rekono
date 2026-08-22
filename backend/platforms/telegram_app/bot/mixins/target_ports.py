"""Steps that ask which port of a target to work with, or create a new one.

The ports belong to a target, so these steps need the target to have been chosen
before.
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
from users.models import User


class TargetPortMixin(BaseMixin):
    """Steps that choose the port of a target, or create it.

    Attributes:
        all_target_ports: Answer that scans the whole target instead of one of its
          ports.
    """

    all_target_ports = "🌐 All ports"

    @sync_to_async
    def _get_target_ports_keyboard_async(self, target: Target, user: User) -> list[InlineKeyboardButton]:
        """Get one button per port of a target, with its path if it has one.

        Args:
            target: Target whose ports are asked for.
            user: User that answered, who must be a member of its project.

        Returns:
            The buttons, or none of them if the user can't see that target.
        """
        return [
            InlineKeyboardButton(f"{tp.port} - {tp.path}" if tp.path else str(tp.port), callback_data=tp.id)
            for tp in TargetPort.objects.filter(target=target, target__project__members=user).order_by("port")
        ]

    async def ask_for_target_port(self, update: Update, context: CallbackContext) -> int:
        """Ask the users to choose one port of the target, or all of them.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            The step that saves the answer, the step after it if the target has no
            port defined, or the end of the conversation if the chat can't run the
            command or if no target was chosen.
        """
        chat = await self.get_active_telegram_chat(update)
        if not chat:
            return ConversationHandler.END
        target = self.get_context_value(context, Context.TARGET)
        if not target:
            await self.reply(update, "No target selected")
            return ConversationHandler.END
        keyboard = await self._get_target_ports_keyboard_async(target, chat.user)
        if not keyboard:
            return await self.go_to_next_state(update, context, self.get_next_state(self.save_target_port))
        keyboard.append(InlineKeyboardButton(self.all_target_ports, callback_data=self.all_target_ports))
        await self.reply(update, "Choose target port", reply_markup=InlineKeyboardMarkup([[item] for item in keyboard]))
        return await self.go_to_next_state(update, context, self.get_next_state(self.ask_for_target_port))

    async def save_target_port(self, update: Update, context: CallbackContext) -> int:
        """Remember the port that the users chose, if they chose one.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            The next step of the conversation. Nothing is remembered when the users
            choose to scan the whole target, so the task isn't linked to any port.
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
        """Ask the users to write the port that they want to add to the target.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            The step that creates the port.
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
        """Add the port that the users wrote to the chosen target.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            The next step, the previous one if what the users wrote isn't a valid
            port, or the end of the conversation if no target was chosen.
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
        """Tell the users which port was created and forget the conversation.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            The end of the conversation, since this is its last step.
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
