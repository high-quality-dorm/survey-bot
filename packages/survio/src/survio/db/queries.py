from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from sqlalchemy import select
from survio.db import models


async def create_survey(
    session: AsyncSession,
    title: str,
    description: str | None,
    first_question_id: int = 0,
) -> models.Surveys:
    survey = models.Surveys(
        title=title, description=description, first_question_id=first_question_id
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


async def get_question(
    session: AsyncSession, question_id: int
) -> models.Questions | None:
    query = (
        select(models.Questions)
        .where(models.Questions.id == question_id)
        .options(
            joinedload(models.Questions.answers), joinedload(models.Questions.survey)
        )
    )
    result = await session.execute(query)
    return result.unique().scalars().one_or_none()


async def create_user(session: AsyncSession, tg_id: int, name: str) -> models.Users:
    user = models.Users(tg_id=tg_id, name=name)
    session.add(user)
    await session.flush()
    return user
