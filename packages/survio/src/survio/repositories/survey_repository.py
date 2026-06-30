from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from survio.repositories.base_repository import BaseRepository
from survio.db.models import Surveys,Passes,Questions
from typing import Sequence

class SurveyRepository(BaseRepository["Surveys"]):
    async def get_by_uuid(self,uuid:str,session: AsyncSession):
        query = select(self.model).where(self.model.uuid == uuid)

        result = await session.execute(query)
        return result.unique().scalars().one()

    async def get_first_question(self, uuid:str,session:AsyncSession):
        survey = await self.get_by_uuid(uuid,session)
        query = (
            select(Questions)
            .where(Questions.id == survey.first_question_id)
            .options(joinedload(Questions.survey))
        )
        result = await session.execute(query)
        return result.unique().scalars().one()
    
    async def get_passes_by_uuid(self, uuid:str, session:AsyncSession):
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