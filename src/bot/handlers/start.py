from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_i18n import I18nContext

router = Router()


@router.message(CommandStart())
async def handle_cmd_start(message: Message, i18n: I18nContext) -> None:
    assert message.from_user is not None
    await message.answer(i18n.get("cmd-start", name=message.from_user.full_name))
