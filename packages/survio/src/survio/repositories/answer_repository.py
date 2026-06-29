from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from survio.repositories.base_repository import BaseRepository
from survio.db.models import Answers
from typing import Sequence

class AnswerRepository(BaseRepository["Answers"]):
    async def get_with_relationship(self, answer_id: int,session: AsyncSession) -> Answers | None:
        query = (
            select(self.model)
            .where(self.model.id == answer_id)
            .options(
                joinedload(self.model.passes),
                joinedload(self.model.question),
                joinedload(self.model.next_question),
            )
        )
        res = await session.execute(query)
        return res.unique().scalars().one_or_none()