from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject

from bot.db import get_session
from bot.repositories import UserRepository


class DatabaseMiddleware(BaseMiddleware):
    async def __call__(
        self, handler, event: TelegramObject, data: dict[str, Any]
    ) -> Any:
        if not isinstance(event, Message) or not event.from_user:
            return await handler(event, data)

        async with get_session() as session:
            data["user_repo"] = UserRepository(session)

            return await handler(event, data)
