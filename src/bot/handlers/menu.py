from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram_i18n import I18nContext, LazyFilter

from bot.keyboards import get_main_menu_kb, get_to_menu_kb

router = Router()


@router.message(LazyFilter("btn-to-menu"))
@router.message(F.text.lower() == "меню")
@router.message(Command("menu"))
async def handle_menu(message: Message, i18n: I18nContext) -> None:
    assert message.from_user is not None
    await message.answer(i18n.get("menu"), reply_markup=get_main_menu_kb())


@router.message(LazyFilter("btn-menu-create"))
async def handle_menu_create(message: Message, i18n: I18nContext) -> None:
    await message.answer(i18n.get("menu-create"), reply_markup=get_to_menu_kb())


@router.message(LazyFilter("btn-menu-start-survey"))
async def handle_menu_start_survey(message: Message, i18n: I18nContext) -> None:
    await message.answer(i18n.get("menu-start-survey"), reply_markup=get_to_menu_kb())


@router.message(LazyFilter("btn-menu-statistics"))
async def handle_menu_statistics(message: Message, i18n: I18nContext) -> None:
    await message.answer(i18n.get("menu-statistics"), reply_markup=get_to_menu_kb())
