from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db import get_session
from bot.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def create_user(self, tg_id: int, core_id: str) -> User:
        async with get_session() as session:
            user = User(tg_id=tg_id, core_id=core_id)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    async def get_user(self, tg_id: int) -> User | None:
        async with get_session() as session:
            statement = select(User).filter_by(tg_id=tg_id)
            result = await session.execute(statement)
            return result.scalar_one_or_none()
