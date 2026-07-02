from typing import Sequence

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from survio.db.models import Passes, Questions
from survio.repositories.base_repository import BaseRepository


class PassRepository(BaseRepository["Passes"]):
    async def get_with_relationship(self, id: int, session: AsyncSession) -> Passes|None:
        query = (
            select(self.model)
            .where(self.model.id == id)
            .options(
                joinedload(self.model.answer),
                joinedload(self.model.question).joinedload(Questions.answers),
                joinedload(self.model.question).joinedload(Questions.survey),
                joinedload(self.model.user),
            )
        )
        result = await session.execute(query)
        return result.unique().scalars().one_or_none()

    async def get_user_passes(
        self, survey_id: int, user_id: int, session: AsyncSession
    ) -> Sequence[Passes]:
        query = (
            select(self.model)
            .join(self.model.question)
            .options(
                joinedload(self.model.question).joinedload(Questions.answers),
                joinedload(self.model.answer),
            )
            .where(
                and_(
                    self.model.user_id == user_id,
                    Questions.survey_id == survey_id,
                )
            )
        )

        result = await session.execute(query)
        return result.unique().scalars().all()

    async def delete_user_passes(
        self, survey_id: int, user_id: int, session: AsyncSession
    ) -> None:

        passes = await self.get_user_passes(survey_id, user_id, session)

        for p in passes:
            await session.delete(p)
