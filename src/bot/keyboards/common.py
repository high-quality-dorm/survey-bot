from aiogram_i18n import LazyProxy
from aiogram_i18n.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def get_to_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=LazyProxy("btn-to-menu"))]],
        resize_keyboard=True,
    )


def get_main_menu_kb() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=LazyProxy("btn-menu-create"))],
            [KeyboardButton(text=LazyProxy("btn-menu-start-survey"))],
            [KeyboardButton(text=LazyProxy("btn-menu-statistics"))],
        ],
        resize_keyboard=True,
    )
