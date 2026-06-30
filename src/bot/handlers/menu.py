from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_i18n import I18nContext

router = Router()


@router.message(F.text.lower() == "меню")
@router.message(Command("menu"))
async def handle_menu(message: Message, i18n: I18nContext) -> None:
    assert message.from_user is not None
    await message.answer(i18n.get("menu"))
