import json
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from survio.schemas import json_schemas, schemas

from .db.queries import (
    create_answer,
    create_pass,
    create_question,
    create_survey,
    create_user,
    get_question,
)


class JSONParser:
    def parse_file(self, file: Path | str) -> json_schemas.SurveyJSON:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return json_schemas.SurveyJSON(**data)

    def parse_str(self, string: str) -> json_schemas.SurveyJSON:
        data = json.loads(string)
        return json_schemas.SurveyJSON(**data)


class SurveyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_question_with_answers(self, question_id: int) -> schemas.Question:
        question = await get_question(self.session, question_id=question_id)
        return schemas.Question.model_validate(question)

    async def create_user(self, id: int) -> schemas.User:
        user = await create_user(self.session, id=id)
        await self.session.commit()
        return schemas.User.model_validate(user)

    async def answer_question(self, answer_id: int, user_id: int) -> schemas.Pass:
        res = await create_pass(self.session, answer_id, user_id)
        await self.session.commit()
        return schemas.Pass.model_validate(res)

    async def answer_and_get_next_question(
        self, answer_id: int, user_id: int
    ) -> schemas.Question | None:
        pass_schema = await self.answer_question(answer_id=answer_id, user_id=user_id)

        if pass_schema is not None:
            nxt_qstn_id = pass_schema.answer.next_question_id
            if nxt_qstn_id is not None:
                res = await get_question(self.session, question_id=nxt_qstn_id)
            else:
                return None
        else:
            return None
        return schemas.Question.model_validate(res)

    async def create_survey_in_db(self, survey_data: json_schemas.SurveyJSON) -> str:
        survey = await create_survey(
            self.session, title=survey_data.title, description=survey_data.description
        )
        questions = dict()
        for q in survey_data.questions:
            question = await create_question(
                self.session, question=q.question, survey_id=survey.id
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
                    self.session,
                    qstn_id=qstn[0].id,
                    nxt_qstn_id=next_q_id,
                    answer=ans.answer,
                )
        await self.session.commit()
        return survey.uuid

    async def parse_and_create_survey(self, json_data: Path | str) -> str:
        parser = JSONParser()
        if isinstance(json_data, Path):
            survey_data = parser.parse_file(json_data)
        else:
            if ".json" in json_data:
                survey_data = parser.parse_file(json_data)
            else:
                survey_data = parser.parse_str(json_data)

        return await self.create_survey_in_db(survey_data)
