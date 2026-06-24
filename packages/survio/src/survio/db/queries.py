import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from survio.db import models
from survio.schemas import schemas


async def create_survey(session: AsyncSession, survey_json: schemas.SurveyJSON):
    survey = models.Surveys(
        uuid=str(uuid.uuid4()), title=survey_json.title, description=survey_json.description
    )
    session.add(survey)
    await session.flush()
    questions = dict()
    for q in survey_json.questions:
        question = models.Questions(question=q.question, survey_id=survey.id)
        questions[q.name] = (question, q.answers)
    session.add_all([q[0] for q in questions.values()])
    await session.flush()
    for q in questions.values():
        for ans in q[1]:
            answer = models.Answers(
                question_id=q[0].id,
                next_question_id=questions.get(ans.next_question)[0].id,
                answer=ans.answer,
            )
            session.add(answer)
    await session.commit()
