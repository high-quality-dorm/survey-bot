import json
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from .db.database import get_session
from .db.queries import create_survey, create_question, create_answer, get_question
from survio.schemas import json_schemas, schemas


class JSONParser:
    def __init__(self, file: Path):
        self.filepath = file

    def parse(self) -> json_schemas.SurveyJSON:
        with open(self.filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        return json_schemas.SurveyJSON(**data)

    async def create_survey_in_db(self, session: AsyncSession) -> str:
        survey_json = self.parse()
        survey = await create_survey(
            session, title=survey_json.title, description=survey_json.description
        )
        questions = dict()
        for q in survey_json.questions:
            question = await create_question(
                session, question=q.question, survey_id=survey.id
            )
            if survey.first_question_id == 0:
                survey.first_question_id = question.id
            questions[q.name] = (question, q.answers)
        for qstn in questions.values():
            for ans in qstn[1]:
                if ans.next_question is None:
                    next_q_id = None
                else:
                    next_question_data = questions.get(ans.next_question)
                    if next_question_data is not None:
                        next_q_id = next_question_data[0].id
                    else:
                        next_q_id = None

                await create_answer(
                    session,
                    qstn_id=qstn[0].id,
                    nxt_qstn_id=next_q_id,
                    answer=ans.answer,
                )
        await session.commit()
        return survey.uuid


class SurveyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_question_with_answers(self, question_id: int) -> schemas.Question:
        question = await get_question(self.session, question_id=question_id)
        return schemas.Question.model_validate(question)


if __name__ == "__main__":
    import asyncio
    from survio.db.database import create_tables

    async def main():
        await create_tables()

        async for session in get_session():
            survey_repo = SurveyRepository(session)
            print(await survey_repo.get_question_with_answers(2))
            break

    asyncio.run(main())
