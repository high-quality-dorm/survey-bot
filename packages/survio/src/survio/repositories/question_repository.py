from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from survio.repositories.base_repository import BaseRepository


class QuestionRepository(BaseRepository["User"]):
    async def get_with_relationship(self, id: int, session: AsyncSession):
        query = (
            select(self.model.Questions)
            .where(self.model.Questions.id == id)
            .options(
                joinedload(self.model.Questions.answers),
                joinedload(self.model.Questions.survey),
            )
        )
        result = await session.execute(query)
        return result.unique().scalars().one_or_none()
