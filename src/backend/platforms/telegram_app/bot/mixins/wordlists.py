from asgiref.sync import sync_to_async
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, ConversationHandler

from input_types.enums import InputTypeName
from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.bot.mixins.framework import BaseMixin
from tools.models import Input
from wordlists.models import Wordlist


class WordlistMixin(BaseMixin):
    default_wordlist = "Default tools wordlists"
    tools_with_required_wordlists = ["Gobuster"]

    @sync_to_async
    def _get_wordlists_keyboard_async(self) -> list[InlineKeyboardButton]:
        return [InlineKeyboardButton(f"{w.name} - {w.type}", callback_data=w.id) for w in Wordlist.objects.all()]

    async def ask_for_wordlist(self, update: Update, context: CallbackContext) -> int:
        self.validate_update(update)
        tool = self.get_context_value(context, Context.TOOL)
        process = self.get_context_value(context, Context.PROCESS)
        if not tool and not process:
            self.reply(update, "No tool or process selected")
            return ConversationHandler.END
        if (
            tool
            and not await self.queryset_exists_async(
                Input.objects.filter(argument__tool=tool, type__name=InputTypeName.WORDLIST)
            )
        ) or (
            process
            and not await self.queryset_exists_async(
                Input.objects.filter(
                    argument__tool__in=process.steps.all().values("configuration__tool"),
                    type__name=InputTypeName.WORDLIST,
                )
            )
        ):
            return await self.go_to_next_state(update, context, self.get_next_state(self.save_wordlist))
        keyboard = await self._get_wordlists_keyboard_async()
        required_filter = {"argument__required": True, "type__name": InputTypeName.WORDLIST}
        is_wordlist_required = (
            tool
            and (
                tool.name in self.tools_with_required_wordlists
                or await self.queryset_exists_async(Input.objects.filter(**{**required_filter, "argument__tool": tool}))
            )
            or (
                process
                and (
                    await self.queryset_exists_async(
                        process.steps.filter(configuration__tool__name__in=self.tools_with_required_wordlists)
                    )
                    or await self.queryset_exists_async(
                        Input.objects.filter(
                            **{
                                **required_filter,
                                "argument__tool__in": process.steps.all().values("configuration__tool"),
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
        self.validate_update(update)
        if update.callback_query and update.callback_query.data and update.callback_query.data == self.default_wordlist:
            await update.callback_query.answer()
            return await self.go_to_next_state(update, context, self.get_next_state(self.save_wordlist))
        else:
            return await self.go_to_next_state(
                update,
                context,
                await self.save(update, context, Context.WORDLIST, Wordlist, self.get_next_state(self.save_wordlist)),
            )
