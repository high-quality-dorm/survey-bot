from asyncio import CancelledError

from aiogram import Bot, Dispatcher

from bot.core import settings

bot = Bot(token=settings.token)
dp = Dispatcher(drop_pending_updates=True)


async def run() -> None:
    try:
        print("bot started")
        await dp.start_polling(bot)
    except (KeyboardInterrupt, CancelledError):
        ...
    finally:
        await bot.session.close()
        print("bot stopped")
