from sqlalchemy.ext.asyncio import AsyncSession
from survio.repositories.pass_repository import PassRepository
from survio.db.models import Passes
from survio.schemas import schemas

class PassService:
    def __init__(self):
        self.repo = PassRepository(Passes)

    async def get(self, pass_id: int, session: AsyncSession) -> schemas.Pass | None:
        pass_obj = await self.repo.get_with_relationship(pass_id, session)
        if pass_obj is None:
            return None
        return schemas.Pass.model_validate(pass_obj)

    async def get_user_passes(
        self, survey_id: int, user_id: int, session: AsyncSession
    ) -> list[schemas.Pass]:
        passes = await self.repo.get_user_passes(survey_id, user_id, session)
        return [schemas.Pass.model_validate(p) for p in passes]