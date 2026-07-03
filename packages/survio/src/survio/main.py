import json
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from survio.schemas import json_schemas, schemas
from survio.services.answer_service import AnswerService
from survio.services.pass_service import PassService
from survio.services.survey_service import SurveyService
from survio.services.user_service import UserService


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


class SurveyEngine:
    def __init__(self, user_id: int, session: AsyncSession):
        self.session = session
        self.survey_service = SurveyService()
        self.pass_service = PassService()
        self.user_service = UserService()
        self.answer_service = AnswerService()
        self.user: schemas.User | None = None
        self.question: schemas.Question | None = None
        self._user_id: int = user_id

    async def init(self) -> None:
        user = await self.user_service.get(self._user_id, self.session)
        if user is None:
            self.user = await self.user_service.create(self._user_id, self.session)
        else:
            self.user = user
        await self.session.commit()

    async def get_survey(self, survey_uuid: str) -> schemas.Survey:
        survey = await self.survey_service.get_by_uuid(survey_uuid, self.session)
        return survey

    async def load_survey(self, survey: Path | str) -> str:
        if isinstance(survey, Path):
            survey_data = JSONParser.parse_file(survey)
        else:
            survey_data = JSONParser.parse_str(survey)
        return await self.survey_service.create_survey_from_json(
            survey_data, self.session
        )

    async def start_survey(self, survey_uuid: str) -> schemas.Question:
        self.question = await self.survey_service.get_first_question(
            survey_uuid, self.session
        )
        return self.question

    def get_current_question(self) -> schemas.Question | None:
        return self.question

    async def submit_answer(
        self, answer_id: int, answer: str | None = None
    ) -> schemas.Question | None:
        if self.user is None:
            await self.init()
        answer_obj = await self.answer_service.get(answer_id, self.session)
        if answer_obj.answer is None and answer is not None:
            question_id = answer_obj.question_id
            new_answer = await self.answer_service.create_answer(
                question_id=None,
                next_question_id=answer_obj.next_question_id,
                answer=answer,
                session=self.session,
            )
            await self.survey_service.submit_answer(
                new_answer.id, self._user_id, self.session, question_id=question_id
            )
        if answer_obj.answer is not None:
            await self.survey_service.submit_answer(
                answer_id, self._user_id, self.session
            )
        next_q_id = answer_obj.next_question_id
        if next_q_id is None:
            self.question = None
            return None

        self.question = await self.survey_service.get_question_with_answers(
            next_q_id, self.session
        )
        return self.question

    def _pass_2_answerext(self, pass_: schemas.Pass) -> schemas.AnswerExt:
        return schemas.AnswerExt(
            id=pass_.answer.id,
            answer=pass_.answer.answer,
            next_question_id=pass_.answer.next_question_id,
            question_id=pass_.question_id,
            question=pass_.question,
        )

    async def get_survey_result(self, survey_uuid: str) -> schemas.SurveyResult:
        if self.user is None:
            await self.init()

        return await self.survey_service.get_survey_result(
            survey_uuid, self._user_id, self.session
        )

    async def get_all_results(self, survey_uuid: str) -> list[schemas.SurveyResult]:
        return await self.survey_service.get_all_survey_results(
            survey_uuid, self.session
        )

    async def get_statistics(self, survey_uuid: str) -> dict[str, dict[str, int]]:
        results = await self.get_all_results(survey_uuid)
        stats: dict[str, dict] = {}

        questions = []  # get questions from service, not results

        for result in results:
            answers = result.answers
            for answer in answers:
                questions.append(answer.question)
                stats[answer.question.question] = stats.get(
                    answer.question.question, {}
                )
                assert answer.answer is not None
                stats[answer.question.question][answer.answer] = (
                    stats[answer.question.question].get(answer.answer, 0) + 1
                )
        return stats

    async def get_user_passes(self, survey_id: int) -> list[schemas.Pass]:
        if self.user is None:
            await self.init()
        return await self.pass_service.get_user_passes(
            survey_id, self._user_id, self.session
        )

    async def delete_user_passes(self, survey_uuid: str) -> None:
        if self.user is None:
            await self.init()
        await self.survey_service.delete_user_passes(
            survey_uuid, self._user_id, self.session
        )

    async def update_survey(
        self, survey_uuid: str, survey_data: json_schemas.SurveyJSON
    ) -> None:
        await self.survey_service.update_survey(survey_uuid, survey_data, self.session)
