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


async def get_answer(session: AsyncSession, answer_id: int) -> models.Answers | None:
    query = select(models.Answers).where(models.Answers.id == answer_id)
    res = await session.execute(query)
    return res.scalars().one_or_none()


async def get_user_by_tg_id(session: AsyncSession, tg_id: int) -> models.Users | None:
    query = select(models.Users).where(models.Users.tg_id == tg_id)
    res = await session.execute(query)
    return res.scalars().one_or_none()


async def create_pass(
    session: AsyncSession, answer_id: int, tg_id: int
) -> models.Passes | None:
    ans = await get_answer(session=session, answer_id=answer_id)
    if ans is not None:
        question_id = ans.question_id
    else:
        return None
    user = await get_user_by_tg_id(session=session, tg_id=tg_id)
    if user is not None:
        res = models.Passes(
            user_id=user.id, question_id=question_id, answer_id=answer_id
        )
    else:
        return None
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
