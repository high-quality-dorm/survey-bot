import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from survio.db import models


async def create_survey(
    session: AsyncSession, title: str, description: str | None
) -> models.Surveys:
    survey = models.Surveys(
        uuid=str(uuid.uuid4()), title=title, description=description
    )
    session.add(survey)
    await session.flush()
    return survey


async def create_question(
    session: AsyncSession, question: str, survey_id
) -> models.Questions:
    qstn = models.Questions(question=question, survey_id=survey_id)
    session.add(qstn)
    await session.flush()
    return qstn


async def create_answer(
    session: AsyncSession, qstn_id: int, nxt_qstn_id: int | None, answer: str | None
) -> models.Answers:
    ans = models.Answers(
        question_id=qstn_id,
        next_question_id=nxt_qstn_id,
        answer=answer,
    )
    session.add(ans)
    await session.flush()
    return ans
