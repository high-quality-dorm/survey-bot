from sqlalchemy.ext.asyncio import AsyncSession

from survio.db.models import Users
from survio.repositories.base_repository import BaseRepository
from survio.schemas import schemas


class UserService:
    def __init__(self):
        self.repo = BaseRepository(Users)

    async def get(self, user_id: int, session: AsyncSession) -> schemas.User | None:
        user = await self.repo.get(user_id, session)
        if user is None:
            return None
        return schemas.User.model_validate(user)

    async def get_all(self, session: AsyncSession) -> list[schemas.User]:
        users = await self.repo.get_all(session)
        return [schemas.User.model_validate(u) for u in users]

    async def create(self, user_id: int, session: AsyncSession) -> schemas.User:
        user = Users(id=user_id)
        await self.repo.create(user, session)
        await session.commit()
        return schemas.User.model_validate(user)
