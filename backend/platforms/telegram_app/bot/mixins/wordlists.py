"""Telegram Bot mixin for wordlist selection workflows.

Provides wordlist selection functionality for conversations that require
wordlist context including conditional wordlist requirements and default options.
Expects either Context.CONFIGURATION (Tool conversation) or Context.PROCESS
(Process conversation) to already be set, since that determines whether any of
the tool's or process's arguments actually take a wordlist, and whether one is
required. Leaves Context.WORDLIST set, or unset when the default wordlist is kept.
"""

from asgiref.sync import sync_to_async
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, ConversationHandler

from input_types.enums import InputTypeName
from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.bot.mixins.framework import BaseMixin
from tools.models import Input
from wordlists.models import Wordlist


class WordlistMixin(BaseMixin):
    """Mixin providing wordlist selection functionality for bot conversations.

    Enables conversations to display available wordlists and handle wordlist
    selection with conditional requirements based on selected tools or processes.

    Attributes:
        default_wordlist (str): Label for default wordlist option.
    """

    default_wordlist = "Default tools wordlists"

    @sync_to_async
    def _get_wordlists_keyboard_async(self) -> list[InlineKeyboardButton]:
        """Generate keyboard buttons for available wordlists (async wrapper).

        Returns:
            list[InlineKeyboardButton]: Buttons for available wordlists.
        """
        return [InlineKeyboardButton(f"{w.name} - {w.type}", callback_data=w.id) for w in Wordlist.objects.all()]

    async def ask_for_wordlist(self, update: Update, context: CallbackContext) -> int:
        """Display wordlist selection options based on tool/process requirements.

        Shows available wordlists with conditional logic for required vs optional
        wordlist selection based on selected tools or processes.

        Args:
            update (Update): The Telegram update containing user interaction.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int: Next conversation state or ConversationHandler.END.
        """
        self.validate_update(update)
        configuration = self.get_context_value(context, Context.CONFIGURATION)
        process = self.get_context_value(context, Context.PROCESS)
        if not configuration and not process:
            await self.reply(update, "No configuration or process selected")
            return ConversationHandler.END
        if (
            configuration
            and not await self.queryset_exists_async(
                Input.objects.filter(argument__configuration=configuration, type__name=InputTypeName.WORDLIST)
            )
        ) or (
            process
            and not await self.queryset_exists_async(
                Input.objects.filter(
                    argument__configuration__in=process.steps.all().values("configuration"),
                    type__name=InputTypeName.WORDLIST,
                )
            )
        ):
            return await self.go_to_next_state(update, context, self.get_next_state(self.save_wordlist))
        keyboard = await self._get_wordlists_keyboard_async()
        required_filter = {"argument__required": True, "type__name": InputTypeName.WORDLIST}
        is_wordlist_required = (
            configuration
            and (
                await self.queryset_exists_async(
                    Input.objects.filter(**{**required_filter, "argument__configuration": configuration})
                )
            )
            or (
                process
                and (
                    await self.queryset_exists_async(
                        Input.objects.filter(
                            **{
                                **required_filter,
                                "argument__configuration__in": process.steps.all().values("configuration"),
                            }
                        )
                    )
                )
            )
        )
        if not is_wordlist_required:
            keyboard.append(InlineKeyboardButton(self.default_wordlist, callback_data=self.default_wordlist))
        await self.reply(update, "Choose wordlist", reply_markup=InlineKeyboardMarkup([[item] for item in keyboard]))
        return await self.go_to_next_state(update, context, self.get_next_state(self.ask_for_wordlist))

    async def save_wordlist(self, update: Update, context: CallbackContext) -> int:
        """Save selected wordlist to conversation context.

        Processes wordlist selection including handling of default wordlist option
        and storing selected wordlist in conversation context.

        Args:
            update (Update): The Telegram update containing wordlist selection.
            context (CallbackContext): The callback context for the conversation.

        Returns:
            int: Next conversation state after wordlist selection.
        """
        self.validate_update(update)
        if update.callback_query and update.callback_query.data and update.callback_query.data == self.default_wordlist:
            await update.callback_query.answer()
            return await self.go_to_next_state(update, context, self.get_next_state(self.save_wordlist))
        return await self.go_to_next_state(
            update,
            context,
            await self.save(update, context, Context.WORDLIST, Wordlist, self.get_next_state(self.save_wordlist)),
        )
