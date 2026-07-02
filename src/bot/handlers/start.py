from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_i18n import I18nContext

from bot.keyboards import get_to_menu_kb
from bot.repositories import UserRepository

router = Router()


@router.message(CommandStart())
async def handle_cmd_start(
    message: Message,
    i18n: I18nContext,
    user_repo: UserRepository,
) -> None:
    assert message.from_user is not None

    await user_repo.get_or_create_user(tg_id=message.from_user.id, core_id=None)

    await message.answer(
        text=i18n.get("cmd-start", name=message.from_user.full_name),
        reply_markup=get_to_menu_kb(),
    )
