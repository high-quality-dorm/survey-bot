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
    get_first_question,
    get_passes_by_uuid,
    get_question,
    get_survey_by_uuid,
    get_user_passes,
    get_user
)


class JSONParser:

    @staticmethod
    def parse_file(file: Path | str) -> json_schemas.SurveyJSON:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return json_schemas.SurveyJSON(**data)
    
    @staticmethod
    def parse_str(string: str) -> json_schemas.SurveyJSON:
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

    async def survey_by_uuid(self, uuid: str) -> schemas.Survey:
        survey = await get_survey_by_uuid(self.session, uuid)
        return schemas.Survey.model_validate(survey)

    async def first_question(self, uuid: str) -> schemas.Question:
        question = await get_first_question(self.session, uuid)
        return schemas.Question.model_validate(question)

    async def user_passes(self, survey_id: int, user_id: int) -> list[schemas.Pass]:
        passes = await get_user_passes(self.session, survey_id, user_id)
        return [schemas.Pass.model_validate(i) for i in passes]

    async def passes_by_uuid(self, uuid: str) -> list[schemas.Pass]:
        passes = await get_passes_by_uuid(self.session, uuid)
        return [schemas.Pass.model_validate(p) for p in passes]

    async def get_user(self, user_id: int) -> schemas.User|None:
        user = await self.get_user(self.session, user_id)
        if user is None:
            return None
        else:
            return schemas.User.model_validate(user)
        
class SurveyEngine:
    def __init__(self, session: AsyncSession, user_id: int):
        self.session = session
        self.repository = SurveyRepository(session)
        user = self.repository.get_user(user_id)
        self.question = None

        if user is None:
            self.user = self.repository.create_user(user_id)
        else:
            self.user = user

    async def get_survey(self, survey_uuid: str) -> schemas.Survey:
        return await self.repository.survey_by_uuid(survey_uuid)
    
    async def load_survey(self, survey: Path|str) -> str:
        if isinstance(survey, Path):
            survey_data = JSONParser.parse_file(survey)
        else:
            if ".json" in survey:
                survey_data = JSONParser.parse_file(survey)
            else:
                survey_data = JSONParser.parse_str(survey)

        return await self.repository.create_survey_in_db(survey_data)
    
    async def start_survey(self, survey_uuid: str) -> schemas.Question:
        self.question = await self.repository.first_question(survey_uuid)
        return self.question
    
    def get_current_question(self) -> schemas.Question|None:
        return self.question
    
    async def submit_answer(self, answer_id:int) -> schemas.Question:
        self.question = await self.repository.answer_and_get_next_question(answer_id,self.user.id)
        return self.question
    
    async def get_survey_result(self, survey_uuid:int) -> schemas.SurveyResult:
        passes = await self.repository.user_passes(survey_uuid, self.user.id)
        #add pydantic validate from list[Pass] to SurveyResult