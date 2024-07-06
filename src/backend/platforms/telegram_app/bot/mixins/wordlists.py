from asgiref.sync import sync_to_async
from input_types.enums import InputTypeName
from platforms.telegram_app.bot.enums import Context
from platforms.telegram_app.bot.mixins.framework import BaseMixin
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
from tools.models import Input
from wordlists.models import Wordlist


class WordlistMixin(BaseMixin):
    default_wordlist = "Default tools wordlists"

    @sync_to_async
    def _get_wordlists_keyboard_async(self) -> list[InlineKeyboardButton]:
        return [
            InlineKeyboardButton(f"{w.name} - {w.type}", callback_data=w.id)
            for w in Wordlist.objects.all()
        ]

    async def _ask_for_wordlist(self, update: Update, context: CallbackContext) -> int:
        tool = self._get_context_value(context, Context.TOOL)
        process = self._get_context_value(context, Context.PROCESS)
        if (
            tool
            and not await self._queryset_exists_async(
                Input.objects.filter(
                    argument__tool=tool, type__name=InputTypeName.WORDLIST
                )
            )
        ) or (
            process
            and not await self._queryset_exists_async(
                Input.objects.filter(
                    argument__tool__in=process.steps.all().values(
                        "configuration__tool"
                    ),
                    type__name=InputTypeName.WORDLIST,
                )
            )
        ):
            return await self._go_to_next_state(
                update, context, self._get_next_state(self._save_wordlist)
            )
        keyboard = await self._get_wordlists_keyboard_async()
        tools_with_required_wordlists = ["Gobuster"]
        required_filter = {
            "argument__required": True,
            "type__name": InputTypeName.WORDLIST,
        }
        is_wordlist_required = (
            tool
            and (
                tool.name in tools_with_required_wordlists
                or await self._queryset_exists_async(
                    Input.objects.filter(**{**required_filter, "argument__tool": tool})
                )
            )
            or (
                process
                and (
                    await self._queryset_exists_async(
                        process.steps.filter(
                            configuration__tool__name__in=tools_with_required_wordlists
                        )
                    )
                    or await self._queryset_exists_async(
                        Input.objects.filter(
                            **{
                                **required_filter,
                                "argument__tool__in": process.steps.all().values(
                                    "configuration__tool"
                                ),
                            }
                        )
                    )
                )
            )
        )
        if not is_wordlist_required:
            keyboard.append(
                InlineKeyboardButton(
                    self.default_wordlist, callback_data=self.default_wordlist
                )
            )
        await self._reply(
            update,
            "Choose wordlist",
            reply_markup=InlineKeyboardMarkup([[item] for item in keyboard]),
        )
        return await self._go_to_next_state(
            update, context, self._get_next_state(self._ask_for_wordlist)
        )

    async def _save_wordlist(self, update: Update, context: CallbackContext) -> int:
        if (
            update.callback_query
            and update.callback_query.data
            and update.callback_query.data == self.default_wordlist
        ):
            await update.callback_query.answer()
            return await self._go_to_next_state(
                update, context, self._get_next_state(self._save_wordlist)
            )
        else:
            return await self._go_to_next_state(
                update,
                context,
                await self._save(
                    update,
                    context,
                    Context.WORDLIST,
                    Wordlist,
                    self._get_next_state(self._save_wordlist),
                ),
            )
