import pytest

from survio.services.survey_service import SurveyService
from survio.schemas import json_schemas
from survio.db.models import Surveys, Questions, Answers, Passes, Users
from survio.repositories.survey_repository import SurveyRepository
from survio.repositories.question_repository import QuestionRepository
from survio.repositories.answer_repository import AnswerRepository
from survio.repositories.pass_repository import PassRepository
from survio.repositories.user_repository import  UserRepository

@pytest.fixture
def survey_service():
    return SurveyService()

@pytest.fixture
def sample_survey_json():
    return {
        "title": "Test Survey",
        "description": "Desc",
        "questions": [
            {
                "name": "q1",
                "question": "First question?",
                "type": "button",
                "answers": [
                    {"answer": "Yes", "next_question": "q2"},
                    {"answer": "No", "next_question": None}
                ]
            },
            {
                "name": "q2",
                "question": "Second question?",
                "type": "free_text",
                "answers": [
                    {"answer": None, "next_question": None}
                ]
            }
        ]
    }

@pytest.mark.asyncio
async def test_create_survey_from_json(survey_service, session, sample_survey_json):
    survey_data = json_schemas.SurveyJSON(**sample_survey_json)
    survey_uuid = await survey_service.create_survey_from_json(survey_data, session)
    assert survey_uuid is not None
    survey_repo = SurveyRepository(Surveys)
    survey = await survey_repo.get_by_uuid(survey_uuid, session)
    assert survey is not None
    assert survey.title == "Test Survey"
    question_repo = QuestionRepository(Questions)
    questions = await question_repo.get_all(session)
    questions_in_survey = [q for q in questions if q.survey_id == survey.id]
    assert len(questions_in_survey) == 2
    answer_repo = AnswerRepository(Answers)
    all_answers = await answer_repo.get_all(session)
    answers_in_survey = [a for a in all_answers if a.question_id in [q.id for q in questions_in_survey]]
    assert len(answers_in_survey) == 3

@pytest.mark.asyncio
async def test_get_by_uuid(survey_service, session):
    survey_data = json_schemas.SurveyJSON(
        title="Test",
        description="Desc",
        questions=[]
    )
    sample = {
        "title": "GetByUuid Survey",
        "description": "Desc",
        "questions": [
            {
                "name": "q1",
                "question": "Q?",
                "type": "button",
                "answers": [{"answer": "A", "next_question": None}]
            }
        ]
    }
    survey_data = json_schemas.SurveyJSON(**sample)
    survey_uuid = await survey_service.create_survey_from_json(survey_data, session)
    survey_schema = await survey_service.get_by_uuid(survey_uuid, session)
    assert survey_schema.uuid == survey_uuid
    assert survey_schema.title == "GetByUuid Survey"

@pytest.mark.asyncio
async def test_get_first_question(survey_service, session):
    sample = {
        "title": "First Q Survey",
        "description": "Desc",
        "questions": [
            {
                "name": "q1",
                "question": "First?",
                "type": "button",
                "answers": [{"answer": "A", "next_question": None}]
            },
            {
                "name": "q2",
                "question": "Second?",
                "type": "button",
                "answers": [{"answer": "B", "next_question": None}]
            }
        ]
    }
    survey_data = json_schemas.SurveyJSON(**sample)
    survey_uuid = await survey_service.create_survey_from_json(survey_data, session)
    first_q = await survey_service.get_first_question(survey_uuid, session)
    assert first_q is not None
    assert first_q.question == "First?"

@pytest.mark.asyncio
async def test_submit_answer(survey_service, session):
    sample = {
        "title": "Submit Answer",
        "description": "Desc",
        "questions": [
            {
                "name": "q1",
                "question": "Q1?",
                "type": "button",
                "answers": [
                    {"answer": "Yes", "next_question": "q2"},
                    {"answer": "No", "next_question": None}
                ]
            },
            {
                "name": "q2",
                "question": "Q2?",
                "type": "button",
                "answers": [{"answer": "Ok", "next_question": None}]
            }
        ]
    }
    survey_data = json_schemas.SurveyJSON(**sample)
    survey_uuid = await survey_service.create_survey_from_json(survey_data, session)
    survey_repo = SurveyRepository(Surveys)
    survey = await survey_repo.get_by_uuid(survey_uuid, session)
    user_repo = UserRepository(Users)
    user = Users(id=1)
    await user_repo.create(user, session)
    await session.flush()
    survey = await survey_repo.get_by_uuid(survey_uuid, session)
    assert survey is not None
    question_repo = QuestionRepository(Questions)
    questions = await question_repo.get_all(session)
    q1 = next(q for q in questions if q.survey_id == survey.id and q.question == "Q1?")
    answer_repo = AnswerRepository(Answers)
    answers = await answer_repo.get_all(session)
    ans_yes = next(a for a in answers if a.question_id == q1.id and a.answer == "Yes")
    pass_schema = await survey_service.submit_answer(ans_yes.id, 1, session)
    assert pass_schema is not None
    assert pass_schema.user_id == 1
    assert pass_schema.question_id == q1.id
    assert pass_schema.answer.id == ans_yes.id
    pass_repo = PassRepository(Passes)
    passes = await pass_repo.get_all(session)
    assert len(passes) == 1

@pytest.mark.asyncio
async def test_get_survey_result(survey_service, session):
    sample = {
        "title": "Result Test",
        "description": "Desc",
        "questions": [
            {
                "name": "q1",
                "question": "Q1?",
                "type": "button",
                "answers": [
                    {"answer": "Yes", "next_question": "q2"},
                    {"answer": "No", "next_question": None}
                ]
            },
            {
                "name": "q2",
                "question": "Q2?",
                "type": "button",
                "answers": [{"answer": "Ok", "next_question": None}]
            }
        ]
    }
    survey_data = json_schemas.SurveyJSON(**sample)
    survey_uuid = await survey_service.create_survey_from_json(survey_data, session)
    user_repo = UserRepository(Users)
    user = Users(id=2)
    await user_repo.create(user, session)
    await session.flush()
    survey_repo = SurveyRepository(Surveys)
    survey = await survey_repo.get_by_uuid(survey_uuid, session)
    question_repo = QuestionRepository(Questions)
    questions = await question_repo.get_all(session)
    q1 = next(q for q in questions if q.survey_id == survey.id and q.question == "Q1?")
    q2 = next(q for q in questions if q.survey_id == survey.id and q.question == "Q2?")
    answer_repo = AnswerRepository(Answers)
    answers = await answer_repo.get_all(session)
    ans_yes = next(a for a in answers if a.question_id == q1.id and a.answer == "Yes")
    ans_ok = next(a for a in answers if a.question_id == q2.id and a.answer == "Ok")
    pass_repo = PassRepository(Passes)
    pass1 = Passes(user_id=2, question_id=q1.id, answer_id=ans_yes.id)
    pass2 = Passes(user_id=2, question_id=q2.id, answer_id=ans_ok.id)
    await pass_repo.create(pass1, session)
    await pass_repo.create(pass2, session)
    await session.flush()
    result = await survey_service.get_survey_result(survey_uuid, 2, session)
    assert result is not None
    assert result.user.id == 2
    assert len(result.answers) == 2
    assert result.answers[0].question_id == q1.id
    assert result.answers[1].question_id == q2.id

@pytest.mark.asyncio
async def test_get_all_survey_results(survey_service, session):
    sample = {
        "title": "All Results",
        "description": "Desc",
        "questions": [
            {
                "name": "q1",
                "question": "Q?",
                "type": "button",
                "answers": [{"answer": "A", "next_question": None}]
            }
        ]
    }
    survey_data = json_schemas.SurveyJSON(**sample)
    survey_uuid = await survey_service.create_survey_from_json(survey_data, session)
    user_repo = UserRepository(Users)
    user1 = Users(id=10)
    user2 = Users(id=11)
    await user_repo.create(user1, session)
    await user_repo.create(user2, session)
    await session.flush()
    question_repo = QuestionRepository(Questions)
    q = (await question_repo.get_all(session))[0]
    answer_repo = AnswerRepository(Answers)
    ans = (await answer_repo.get_all(session))[0]
    pass_repo = PassRepository(Passes)
    pass1 = Passes(user_id=10, question_id=q.id, answer_id=ans.id)
    pass2 = Passes(user_id=11, question_id=q.id, answer_id=ans.id)
    await pass_repo.create(pass1, session)
    await pass_repo.create(pass2, session)
    await session.flush()
    results = await survey_service.get_all_survey_results(survey_uuid, session)
    assert len(results) == 2
    user_ids = [r.user.id for r in results]
    assert 10 in user_ids and 11 in user_ids