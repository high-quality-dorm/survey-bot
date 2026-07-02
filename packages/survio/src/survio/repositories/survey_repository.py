from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from survio.db import models
from survio.db.models import Passes, Questions, Surveys #noqa
from survio.repositories.base_repository import BaseRepository


class SurveyRepository(BaseRepository["Surveys"]):
    async def get_by_uuid(
        self, uuid: str, session: AsyncSession
    ) -> models.Surveys | None:
        query = select(self.model).where(self.model.uuid == uuid)

        result = await session.execute(query)
        return result.unique().scalars().one_or_none()

    async def get_first_question(
        self, uuid: str, session: AsyncSession
    ) -> models.Questions | None:
        survey = await self.get_by_uuid(uuid, session)
        query = (
            select(Questions)
            .where(Questions.id == survey.first_question_id)
            .options(joinedload(Questions.survey), joinedload(Questions.answers))
        )
        result = await session.execute(query)
        return result.unique().scalars().one_or_none()

    async def get_passes_by_uuid(
        self, uuid: str, session: AsyncSession
    ) -> Sequence[models.Passes]:
        query = (
            select(Passes)
            .join(Passes.question)
            .join(Questions.survey)
            .where(self.model.uuid == uuid)
            .options(joinedload(Passes.question), joinedload(Passes.answer))
        )

        result = await session.execute(query)
        return result.unique().scalars().all()

    async def get_survey_passes_user_id(
        self, session: AsyncSession, survey_uuid: str
    ) -> Sequence[int]:
        query = (
            select(Passes.user_id)
            .join(Passes.question)
            .join(Questions.survey)
            .where(self.model.uuid == survey_uuid)
        )
        result = await session.execute(query)
        return result.unique().scalars().all()
