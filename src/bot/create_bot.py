import logging
from asyncio import CancelledError

from aiogram import Bot, Dispatcher

from bot.core import settings
from bot.handlers import main_router

logging.basicConfig(
    format="%(levelname)s [%(asctime)s]: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    level=logging.INFO,
)

bot = Bot(token=settings.token)
dp = Dispatcher(drop_pending_updates=True)

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
