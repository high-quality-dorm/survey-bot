import pytest
import json
from survio.main import SurveyEngine
from survio.schemas import schemas, json_schemas
from survio.db.models import Users, Surveys, Answers
from survio.repositories.user_repository import UserRepository
from survio.repositories.survey_repository import SurveyRepository
from survio.repositories.answer_repository import AnswerRepository
from survio.services.survey_service import SurveyService

@pytest.mark.asyncio
async def test_engine_init(survey_engine, session):
    user_repo = UserRepository(Users)
    user = await user_repo.get(1, session)
    assert user is None

    await survey_engine.init()
    assert survey_engine.user is not None
    assert survey_engine.user.id == 1

    user = await user_repo.get(1, session)
    assert user is not None

@pytest.mark.asyncio
async def test_engine_init_existing_user(survey_engine, session):
    user_repo = UserRepository(Users)
    user = Users(id=1)
    await user_repo.create(user, session)
    await session.flush()

    await survey_engine.init()
    assert survey_engine.user is not None
    assert survey_engine.user.id == 1

@pytest.mark.asyncio
async def test_engine_get_survey(survey_engine, session, sample_survey_json):
    
    survey_service = SurveyService()
    survey_data = json_schemas.SurveyJSON(**sample_survey_json)
    survey_uuid = await survey_service.create_survey_from_json(survey_data, session)

    survey = await survey_engine.get_survey(survey_uuid)
    assert isinstance(survey, schemas.Survey)
    assert survey.uuid == survey_uuid
    assert survey.title == sample_survey_json["title"]

@pytest.mark.asyncio
async def test_engine_load_survey_from_file(survey_engine, tmp_path, sample_survey_json):

    file_path = tmp_path / "survey.json"
    with open(file_path, "w") as f:
        json.dump(sample_survey_json, f)

    uuid = await survey_engine.load_survey(file_path)
    assert uuid is not None

    survey_repo = SurveyRepository(Surveys)
    survey = await survey_repo.get_by_uuid(uuid, survey_engine.session)
    assert survey is not None
    assert survey.title == sample_survey_json["title"]

@pytest.mark.asyncio
async def test_engine_load_survey_from_str(survey_engine, sample_survey_json):

    json_str = json.dumps(sample_survey_json)
    uuid = await survey_engine.load_survey(json_str)
    assert uuid is not None
    survey_repo = SurveyRepository(Surveys)
    survey = await survey_repo.get_by_uuid(uuid, survey_engine.session)
    assert survey is not None

@pytest.mark.asyncio
async def test_engine_start_survey(survey_engine, session, sample_survey_json):

    survey_service = SurveyService()
    survey_data = json_schemas.SurveyJSON(**sample_survey_json)
    survey_uuid = await survey_service.create_survey_from_json(survey_data, session)


    await survey_engine.init()

    question = await survey_engine.start_survey(survey_uuid)
    assert isinstance(question, schemas.Question)
    assert survey_engine.question is not None
    assert survey_engine.question.id == question.id

    assert question.question == "First question?"  

@pytest.mark.asyncio
async def test_engine_get_current_question(survey_engine):

    assert survey_engine.get_current_question() is None

    mock_q = schemas.Question(
        id=1, question="Test", survey=schemas.Survey(id=1, uuid="s", title="T", description="D", first_question_id=1), answers=[]
    )
    survey_engine.question = mock_q
    assert survey_engine.get_current_question() == mock_q

@pytest.mark.asyncio
async def test_engine_submit_answer(survey_engine, session, sample_survey_json):
    
    survey_service = SurveyService()
    survey_data = json_schemas.SurveyJSON(**sample_survey_json)
    survey_uuid = await survey_service.create_survey_from_json(survey_data, session)


    await survey_engine.init()


    first_q = await survey_engine.start_survey(survey_uuid)

    answer_repo = AnswerRepository(Answers)
    answers = await answer_repo.get_all(session)
    
    ans_yes = next(a for a in answers if a.question_id == first_q.id and a.answer == "Yes")

    next_q = await survey_engine.submit_answer(ans_yes.id)

    assert next_q is not None
    assert next_q.question == "Second question?"
    assert survey_engine.question.id == next_q.id

@pytest.mark.asyncio
async def test_engine_submit_answer_finish(survey_engine, session):
   
    sample = {
        "title": "Single Q",
        "description": "Desc",
        "questions": [
            {
                "name": "q1",
                "question": "Q1?",
                "type": "button",
                "answers": [{"answer": "A", "next_question": None}]
            }
        ]
    }
    survey_service = SurveyService()
    survey_data = json_schemas.SurveyJSON(**sample)
    survey_uuid = await survey_service.create_survey_from_json(survey_data, session)

    await survey_engine.init()
    first_q = await survey_engine.start_survey(survey_uuid)

    answer_repo = AnswerRepository(Answers)
    answers = await answer_repo.get_all(session)
    ans = next(a for a in answers if a.question_id == first_q.id)

    next_q = await survey_engine.submit_answer(ans.id)
    assert next_q is None
    assert survey_engine.question is None

@pytest.mark.asyncio
async def test_engine_submit_answer_without_init(survey_engine, session, sample_survey_json):

    survey_service = SurveyService()
    survey_data = json_schemas.SurveyJSON(**sample_survey_json)
    survey_uuid = await survey_service.create_survey_from_json(survey_data, session)

    first_q = await survey_engine.start_survey(survey_uuid)

    answer_repo = AnswerRepository(Answers)
    answers = await answer_repo.get_all(session)
    ans_yes = next(a for a in answers if a.question_id == first_q.id and a.answer == "Yes")

    next_q = await survey_engine.submit_answer(ans_yes.id)
    assert next_q is not None

    assert survey_engine.user is not None

@pytest.mark.asyncio
async def test_engine_get_survey_result(survey_engine, session, sample_survey_json):

    survey_service = SurveyService()
    survey_data = json_schemas.SurveyJSON(**sample_survey_json)
    survey_uuid = await survey_service.create_survey_from_json(survey_data, session)

    await survey_engine.init()

    first_q = await survey_engine.start_survey(survey_uuid)

    answer_repo = AnswerRepository(Answers)
    answers = await answer_repo.get_all(session)
    ans_yes = next(a for a in answers if a.question_id == first_q.id and a.answer == "Yes")
    await survey_engine.submit_answer(ans_yes.id)

    second_q = survey_engine.get_current_question()
    assert second_q is not None
    ans_ok = next(a for a in answers if a.question_id == second_q.id and a.answer == "Ok")
    await survey_engine.submit_answer(ans_ok.id)

    result = await survey_engine.get_survey_result(survey_uuid)
    assert isinstance(result, schemas.SurveyResult)
    assert result.user.id == 1
    assert len(result.answers) == 2

    assert result.answers[0].question_id == first_q.id
    assert result.answers[0].answer == "Yes"

    assert result.answers[1].question_id == second_q.id
    assert result.answers[1].answer == "Ok"

@pytest.mark.asyncio
async def test_engine_get_all_results(survey_engine, session, sample_survey_json):

    sample = {
        "title": "All Results Test",
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

    survey_service = SurveyService()
    survey_data = json_schemas.SurveyJSON(**sample)
    survey_uuid = await survey_service.create_survey_from_json(survey_data, session)

    await survey_engine.init()

    first_q = await survey_engine.start_survey(survey_uuid)
    answer_repo = AnswerRepository(Answers)
    answers = await answer_repo.get_all(session)
    ans = next(a for a in answers if a.question_id == first_q.id)
    await survey_engine.submit_answer(ans.id)

    engine2 = SurveyEngine(user_id=2, session=session)
    await engine2.init()
    await engine2.start_survey(survey_uuid)
    await engine2.submit_answer(ans.id)

    results = await survey_engine.get_all_results(survey_uuid)
    assert len(results) == 2
    user_ids = [r.user.id for r in results]
    assert 1 in user_ids and 2 in user_ids

@pytest.mark.asyncio
async def test_engine_get_user_passes(survey_engine, session, sample_survey_json):

    survey_service = SurveyService()
    survey_data = json_schemas.SurveyJSON(**sample_survey_json)
    survey_uuid = await survey_service.create_survey_from_json(survey_data, session)

    await survey_engine.init()
    first_q = await survey_engine.start_survey(survey_uuid)
    answer_repo = AnswerRepository(Answers)
    answers = await answer_repo.get_all(session)
    ans_yes = next(a for a in answers if a.question_id == first_q.id and a.answer == "Yes")
    await survey_engine.submit_answer(ans_yes.id)

    survey_repo = SurveyRepository(Surveys)
    survey = await survey_repo.get_by_uuid(survey_uuid, session)
    passes = await survey_engine.get_user_passes(survey.id)
    assert len(passes) == 1
    assert passes[0].user_id == 1
    assert passes[0].question_id == first_q.id
    assert passes[0].answer.answer == "Yes"

@pytest.mark.asyncio
async def test_engine_delete_user_passes(survey_engine, session, sample_survey_json):

    survey_service = SurveyService()
    survey_data = json_schemas.SurveyJSON(**sample_survey_json)
    survey_uuid = await survey_service.create_survey_from_json(survey_data, session)

    await survey_engine.init()
    first_q = await survey_engine.start_survey(survey_uuid)
    answer_repo = AnswerRepository(Answers)
    answers = await answer_repo.get_all(session)
    ans_yes = next(a for a in answers if a.question_id == first_q.id and a.answer == "Yes")
    await survey_engine.submit_answer(ans_yes.id)

    survey_repo = SurveyRepository(Surveys)
    survey = await survey_repo.get_by_uuid(survey_uuid, session)
    passes_before = await survey_engine.get_user_passes(survey.id)
    assert len(passes_before) == 1

    await survey_engine.delete_user_passes(survey_uuid)

    passes_after = await survey_engine.get_user_passes(survey.id)
    assert len(passes_after) == 0