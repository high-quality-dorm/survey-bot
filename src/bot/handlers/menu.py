from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram_i18n import I18nContext, LazyFilter

from bot.keyboards import get_main_menu_kb

router = Router()


@router.message(LazyFilter("btn-to-menu"))
@router.message(F.text.lower() == "меню")
@router.message(Command("menu"))
async def handle_menu(message: Message, i18n: I18nContext, state: FSMContext) -> None:
    assert message.from_user is not None
    await message.answer(i18n.get("menu"), reply_markup=get_main_menu_kb())
    await state.clear()
