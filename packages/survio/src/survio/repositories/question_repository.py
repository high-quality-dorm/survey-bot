from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from survio.repositories.base_repository import BaseRepository
from survio.db.models import Questions

class QuestionRepository(BaseRepository["Questions"]):
    async def get_with_relationship(self, id: int, session: AsyncSession) -> Questions|None:
        query = (
            select(self.model)
            .where(self.model.id == id)
            .options(
                joinedload(self.model.answers),
                joinedload(self.model.survey),
            )
        )
        result = await session.execute(query)
        return result.unique().scalars().one_or_none()
