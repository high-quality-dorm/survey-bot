import uuid
from typing import Sequence
from sqlalchemy.ext.asyncio import AsyncSession

from survio.repositories.survey_repository import SurveyRepository
from survio.repositories.question_repository import QuestionRepository
from survio.repositories.answer_repository import AnswerRepository
from survio.repositories.pass_repository import PassRepository
from survio.repositories.user_repository import UserRepository
from survio.db.models import Surveys, Questions, Answers, Passes, Users
from survio.schemas import schemas, json_schemas


class SurveyService:
    def __init__(self):
        self.survey_repo = SurveyRepository(Surveys)
        self.question_repo = QuestionRepository(Questions)
        self.answer_repo = AnswerRepository(Answers)
        self.pass_repo = PassRepository(Passes)
        self.user_repo = UserRepository(Users)

    async def get_by_uuid(self, uuid: str, session: AsyncSession) -> schemas.Survey:
        survey = await self.survey_repo.get_by_uuid(uuid, session)
        return schemas.Survey.model_validate(survey)

    async def get_first_question(self, uuid: str, session: AsyncSession) -> schemas.Question:
        question = await self.survey_repo.get_first_question(uuid, session)
        return schemas.Question.model_validate(question)

    async def get_passes_by_uuid(self, uuid: str, session: AsyncSession) -> list[schemas.Pass]:
        passes = await self.survey_repo.get_passes_by_uuid(uuid, session)
        return [schemas.Pass.model_validate(p) for p in passes]

    async def get_survey_passes_user_ids(self, uuid: str, session: AsyncSession) -> Sequence[int]:
        return await self.survey_repo.get_survey_passes_user_id(session, uuid)

    async def create_survey_from_json(
        self, survey_data: json_schemas.SurveyJSON, session: AsyncSession
    ) -> str:
        survey = Surveys(
            uuid=str(uuid.uuid4()),
            title=survey_data.title,
            description=survey_data.description,
            first_question_id=0,  # временно
        )
        await self.survey_repo.create(survey, session)
        await session.flush()

        questions_map = {}
        for q in survey_data.questions:
            question = Questions(
                question=q.question,
                survey_id=survey.id,
            )
            await self.question_repo.create(question, session)
            await session.flush()

            if survey.first_question_id == 0:
                survey.first_question_id = question.id

            questions_map[q.name] = (question, q.answers)

        for qstn_name, (qstn_obj, answers) in questions_map.items():
            for ans in answers:
                if ans.next_question is None:
                    next_q_id = None
                else:
                    next_question_data = questions_map.get(ans.next_question)
                    if next_question_data is not None:
                        next_q_id = next_question_data[0].id
                    else:
                        next_q_id = None

                answer = Answers(
                    question_id=qstn_obj.id,
                    next_question_id=next_q_id,
                    answer=ans.answer,
                )
                await self.answer_repo.create(answer, session)
                await session.flush()

        await session.commit()
        return survey.uuid
    
    async def submit_answer(
        self, answer_id: int, user_id: int, session: AsyncSession
    ) -> schemas.Pass:
        answer = await self.answer_repo.get_with_relationship(answer_id, session)

        pass_obj = Passes(
            user_id=user_id,
            question_id=answer.question_id,
            answer_id=answer.id,
        )
        await self.pass_repo.create(pass_obj, session)
        await session.flush()

        loaded_pass = await self.pass_repo.get_with_relationship(pass_obj.id, session)
        await session.commit()
        return schemas.Pass.model_validate(loaded_pass)

    async def get_survey_result(
        self, survey_uuid: str, user_id: int, session: AsyncSession
    ) -> schemas.SurveyResult:
        survey = await self.survey_repo.get_by_uuid(survey_uuid, session)

        passes = await self.pass_repo.get_user_passes(survey.id, user_id, session)

        user = await self.user_repo.get(user_id, session)

        result = schemas.SurveyResult(user=schemas.User.model_validate(user), answers=[])

        for p in passes:
            question = await self.question_repo.get_with_relationship(p.question_id, session)
            if question is None:
                continue 

            ans_ext = schemas.AnswerExt(
                id=p.answer.id,
                answer=p.answer.answer,
                next_question_id=p.answer.next_question_id,
                question_id=p.question_id,
                question=schemas.Question.model_validate(question),
            )
            result.answers.append(ans_ext)

        self._sort_answers(survey.first_question_id, result.answers)
        return result

    async def get_all_survey_results(
        self, survey_uuid: str, session: AsyncSession
    ) -> list[schemas.SurveyResult]:
        user_ids = await self.get_survey_passes_user_ids(survey_uuid, session)
        results = []
        for uid in user_ids:
            result = await self.get_survey_result(survey_uuid, uid, session)
            results.append(result)
        return results

    def _rec_sort(self, index:int, answers: list[schemas.AnswerExt]) -> None:
        if index== len(answers) -1:
            return
        id_ = answers[index].next_question_id
        for i in range(index, len(answers)):
            if answers[i].question_id == id_:
                ans = answers.pop(i)
                answers.insert(index + 1, ans)
                break
        self._rec_sort(index+1, answers)

    def _sort_answers(self, frst_qstn_id: int, answers: list[schemas.AnswerExt]) -> None:

        for i in range(len(answers)):
            if answers[i].question_id == frst_qstn_id:
                first = answers.pop(i)
                break
        else:
            return
        answers.insert(0,first)

        self._rec_sort(0,answers)
