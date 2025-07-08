from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from authentications.enums import AuthenticationType
from authentications.serializers import AuthenticationSerializer
from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.bot.mixins.framework import BaseMixin


class AuthenticationMixin(BaseMixin):
    no_authentication = "None"
    new_port_command = "newport"

    async def _ask_for_authentication_type(self, update: Update, context: CallbackContext) -> int:
        values = AuthenticationType.values
        current_command = self._get_context_value(context, Context.COMMAND)
        if current_command and current_command.lower() == self.new_port_command:
            values.append(self.no_authentication)
        return await self._go_to_next_state(
            update,
            context,
            await self._ask_values(
                update,
                values,
                3,
                "Choose authentication type",
                self._get_next_state(self._ask_for_authentication_type),
            ),
        )

    async def _save_authentication_type(self, update: Update, context: CallbackContext) -> int:
        if (
            update.callback_query
            and update.callback_query.data
            and update.callback_query.data == self.no_authentication
        ):
            return await self._go_to_next_state(
                update,
                context,
                self._get_next_state(self._create_authentication),
            )
        else:
            return await self._go_to_next_state(
                update,
                context,
                await self._save_value(
                    update,
                    context,
                    Context.AUTHENTICATION_TYPE,
                    "AuthenticationType",
                    self._get_next_state(self._save_authentication_type),
                ),
            )

    async def _ask_for_new_authentication(self, update: Update, context: CallbackContext) -> int:
        return await self._go_to_next_state(
            update,
            context,
            await self._ask_for_new_attribute(
                update,
                "authentication",
                "'name \- secret'",
                self._get_next_state(self._ask_for_new_authentication),
            ),
        )

    async def _create_authentication(self, update: Update, context: CallbackContext) -> int:
        if not update.effective_message or not update.effective_message.text:
            return ConversationHandler.END
        name = update.effective_message.text
        secret = None
        if name and " - " in name:
            name, secret = name.split(" - ", 1)
        target_port = self._get_context_value(context, Context.TARGET_PORT)
        next_state, instance = await self._create(
            update,
            context,
            AuthenticationSerializer,
            {
                "name": name,
                "secret": secret,
                "type": self._get_context_value(context, Context.AUTHENTICATION_TYPE),
                "target_port": target_port.id if target_port else None,
            },
            self._get_previous_state(self._create_authentication),
            self._get_next_state(self._create_authentication),
        )
        if instance:
            self._add_context_value(context, Context.AUTHENTICATION, instance)
        return await self._go_to_next_state(update, context, next_state)
