from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from survio.repositories.base_repository import BaseRepository
from survio.db.models import Passes,Questions
from typing import Sequence

class PassRepository(BaseRepository["Passes"]):
    async def get_with_relationship(self, id: int, session: AsyncSession):
        query = (
            select(self.model)
            .where(self.model.id == id)
            .options(
                joinedload(self.model.answer),
                joinedload(self.model.question),
                joinedload(self.model.user),
            )
        )
        result = await session.execute(query)
        return result.unique().scalars().one()
    
    async def get_user_passes(
    self, survey_id: int, user_id: int, session: AsyncSession
) -> Sequence[Passes]:
        query = (
            select(self.model)
            .join(self.model.question)
            .options(joinedload(self.model.question), joinedload(self.model.answer))
            .where(
                and_(
                    self.model.user_id == user_id,
                    Questions.survey_id == survey_id,
                )
            )
        )

        result = await session.execute(query)
        return result.unique().scalars().all()