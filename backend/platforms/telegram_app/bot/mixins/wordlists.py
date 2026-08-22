"""Steps that ask which wordlist a task must use.

The question is only asked if what the task will run accepts a wordlist at all,
and the users can only skip it if no tool requires one, so these steps need the
configuration or the process to have been chosen before.
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
    """Steps that choose the wordlist that a task will use.

    Attributes:
        default_wordlist: Answer that keeps the wordlists that each tool uses by
          default, instead of choosing one for all of them.
    """

    default_wordlist = "Default tools wordlists"

    @sync_to_async
    def _get_wordlists_keyboard_async(self) -> list[InlineKeyboardButton]:
        """Get one button per wordlist, named after the wordlist and its type.

        Returns:
            The buttons of the keyboard, whose callback data is the identifier of
            each wordlist.
        """
        return [InlineKeyboardButton(f"{w.name} - {w.type}", callback_data=w.id) for w in Wordlist.objects.all()]

    async def ask_for_wordlist(self, update: Update, context: CallbackContext) -> int:
        """Ask the users to choose a wordlist, if the task can use one.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            The step that saves the answer, the step after it if no tool of the
            task accepts a wordlist, or the end of the conversation if neither a
            configuration nor a process was chosen.
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
        """Remember the wordlist that the users chose, if they chose one.

        Args:
            update: Message that the user wrote.
            context: Data that the conversation remembers.

        Returns:
            The next step of the conversation.
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
