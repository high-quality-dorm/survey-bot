from sqlalchemy.ext.asyncio import AsyncSession

from survio.db.models import Answers
from survio.repositories.answer_repository import AnswerRepository
from survio.schemas import schemas


class AnswerService:
    def __init__(self):
        self.repo = AnswerRepository(Answers)

    async def get(self, answer_id: int, session: AsyncSession) -> schemas.Answer | None:
        answer_obj = await self.repo.get_with_relationship(answer_id, session)
        if answer_obj is None:
            return None
        return schemas.Answer.model_validate(answer_obj)

    async def create_answer(
        self,
        question_id: int | None,
        next_question_id: int | None,
        answer: str | None,
        session: AsyncSession,
    ) -> schemas.Answer:
        answer_obj = Answers(
            question_id=question_id,
            next_question_id=next_question_id,
            answer=answer,
        )
        await self.repo.create(answer_obj, session)
        await session.flush()
        return schemas.Answer.model_validate(answer_obj)
