import logging
from asyncio import CancelledError
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram_i18n import I18nMiddleware
from aiogram_i18n.cores import FluentCompileCore

from bot.core import settings
from bot.handlers import main_router

logging.basicConfig(
    format="%(levelname)s [%(asctime)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

bot = Bot(token=settings.token)
dp = Dispatcher(drop_pending_updates=True)


LOCALES = Path(__file__).resolve().parent / "locales"
i18n_middleware = I18nMiddleware(
    core=FluentCompileCore(path=LOCALES),
    default_locale="ru",
)
i18n_middleware.setup(dp)

dp.include_router(main_router)


async def run() -> None:
    try:
        logging.info("Bot is starting")
        await dp.start_polling(bot)
    except (KeyboardInterrupt, CancelledError):
        logging.warning("Bot received stop signal")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
    finally:
        await bot.session.close()
        logging.info("Bot session closed. Bot stopped")
