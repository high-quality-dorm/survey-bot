import uuid
from typing import Sequence

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from survio.db import models


async def create_survey(
    session: AsyncSession,
    title: str,
    description: str | None,
    first_question_id: int = 0,
) -> models.Surveys:
    survey = models.Surveys(
        uuid=str(uuid.uuid4()),
        title=title,
        description=description,
        first_question_id=first_question_id,
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


async def create_user(session: AsyncSession, id: int) -> models.Users:
    user = models.Users(id=id)
    session.add(user)
    await session.flush()
    return user


async def get_answer(session: AsyncSession, answer_id: int) -> models.Answers | None:
    query = (
        select(models.Answers)
        .where(models.Answers.id == answer_id)
        .options(
            joinedload(models.Answers.passes),
            joinedload(models.Answers.question),
            joinedload(models.Answers.next_question),
        )
    )
    res = await session.execute(query)
    return res.unique().scalars().one_or_none()


async def create_pass(
    session: AsyncSession, answer_id: int, user_id: int
) -> models.Passes | None:
    ans = await get_answer(session=session, answer_id=answer_id)
    if ans is not None:
        question_id = ans.question_id
    else:
        return None
    res = models.Passes(user_id=user_id, question_id=question_id, answer_id=answer_id)
    session.add(res)
    await session.flush()

    query = (
        select(models.Passes)
        .where(models.Passes.id == res.id)
        .options(
            joinedload(models.Passes.answer),
            joinedload(models.Passes.question),
            joinedload(models.Passes.user),
        )
    )
    result = await session.execute(query)
    return result.unique().scalars().one()


async def get_survey_by_uuid(session: AsyncSession, uuid: str) -> models.Surveys:
    query = select(models.Surveys).where(models.Surveys.uuid == uuid)

    result = await session.execute(query)
    return result.unique().scalars().one()


async def get_first_question(session: AsyncSession, uuid: str) -> models.Questions:
    survey = await get_survey_by_uuid(session, uuid)
    query = (
        select(models.Questions)
        .where(models.Questions.id == survey.first_question_id)
        .options(joinedload(models.Questions.survey))
    )
    result = await session.execute(query)
    return result.unique().scalars().one()


async def get_user_passes(
    session: AsyncSession, survey_id: int, user_id: int
) -> Sequence[models.Passes]:
    query = (
        select(models.Passes)
        .join(models.Passes.question)
        .options(joinedload(models.Passes.question), joinedload(models.Passes.answer))
        .where(
            and_(
                models.Passes.user_id == user_id,
                models.Questions.survey_id == survey_id,
            )
        )
    )

    result = await session.execute(query)
    return result.unique().scalars().all()


async def get_passes_by_uuid(
    session: AsyncSession, uuid: str
) -> Sequence[models.Passes]:
    query = (
        select(models.Passes)
        .join(models.Passes.question)
        .join(models.Questions.survey)
        .where(models.Surveys.uuid == uuid)
        .options(joinedload(models.Passes.question), joinedload(models.Passes.answer))
    )

    result = await session.execute(query)
    return result.unique().scalars().all()
