from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from survio.main import JSONParser, SurveyEngine
from survio.schemas import json_schemas, schemas


@pytest.fixture
def mock_session():
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.flush = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def engine(mock_session):
    return SurveyEngine(session=mock_session, user_id=1)


@pytest.mark.asyncio
async def test_init_user_exists(mocker, engine):

    mock_user = schemas.User(id=1)
    mocker.patch.object(engine.repository, "get_user", return_value=mock_user)

    create_user_mock = AsyncMock()
    mocker.patch.object(engine.repository, "create_user", new=create_user_mock)

    await engine.init()

    assert engine.user == mock_user
    engine.repository.get_user.assert_awaited_once_with(1)
    create_user_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_init_user_not_exists(mocker, engine):

    mock_user = schemas.User(id=1)
    mocker.patch.object(engine.repository, "get_user", return_value=None)
    mocker.patch.object(engine.repository, "create_user", return_value=mock_user)

    await engine.init()

    assert engine.user == mock_user
    engine.repository.get_user.assert_awaited_once_with(1)
    engine.repository.create_user.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_get_survey(mocker, engine):

    mock_survey = schemas.Survey(id=1, uuid="test", title="Test", description="Desc")
    mocker.patch.object(engine.repository, "survey_by_uuid", return_value=mock_survey)

    result = await engine.get_survey("test-uuid")

    assert result == mock_survey
    engine.repository.survey_by_uuid.assert_awaited_once_with("test-uuid")


@pytest.mark.asyncio
async def test_load_survey_from_path(mocker, engine, tmp_path):

    survey_data = json_schemas.SurveyJSON(
        title="Test",
        description="Desc",
        questions=[
            json_schemas.QuestionJSON(
                name="q1",
                question="Q?",
                answers=[json_schemas.AnswerJSON(answer="A", next_question=None)],
            )
        ],
    )
    mocker.patch.object(JSONParser, "parse_file", return_value=survey_data)
    mocker.patch.object(
        engine.repository, "create_survey_in_db", return_value="uuid-123"
    )

    file_path = tmp_path / "survey.json"
    file_path.write_text("{}")

    result = await engine.load_survey(file_path)

    assert result == "uuid-123"
    JSONParser.parse_file.assert_called_once_with(file_path)
    engine.repository.create_survey_in_db.assert_awaited_once_with(survey_data)


@pytest.mark.asyncio
async def test_load_survey_from_str(mocker, engine):

    survey_data = json_schemas.SurveyJSON(
        title="Test", description="Desc", questions=[]
    )
    mocker.patch.object(JSONParser, "parse_str", return_value=survey_data)
    mocker.patch.object(
        engine.repository, "create_survey_in_db", return_value="uuid-456"
    )

    result = await engine.load_survey('{"title": "Test"}')

    assert result == "uuid-456"
    JSONParser.parse_str.assert_called_once_with('{"title": "Test"}')
    engine.repository.create_survey_in_db.assert_awaited_once_with(survey_data)


@pytest.mark.asyncio
async def test_start_survey(mocker, engine):

    mock_question = schemas.Question(
        id=1,
        question="Q?",
        survey=schemas.Survey(id=1, uuid="s", title="T", description="D"),
        answers=[],
    )
    mocker.patch.object(engine.repository, "first_question", return_value=mock_question)

    result = await engine.start_survey("survey-uuid")

    assert result == mock_question
    assert engine.question == mock_question
    engine.repository.first_question.assert_awaited_once_with("survey-uuid")


@pytest.mark.asyncio
async def test_submit_answer(mocker, engine):

    mock_next_question = schemas.Question(
        id=2,
        question="Next?",
        survey=schemas.Survey(id=1, uuid="s", title="T", description="D"),
        answers=[],
    )

    engine.user = schemas.User(id=1)

    mocker.patch.object(engine, "init", new=AsyncMock())
    mocker.patch.object(
        engine.repository,
        "answer_and_get_next_question",
        return_value=mock_next_question,
    )

    result = await engine.submit_answer(answer_id=5)

    assert result == mock_next_question
    assert engine.question == mock_next_question
    engine.init.assert_not_awaited()
    engine.repository.answer_and_get_next_question.assert_awaited_once_with(
        5, engine.user.id
    )


@pytest.mark.asyncio
async def test_get_survey_result(mocker, engine):
    engine.user = schemas.User(id=1)

    mock_survey = schemas.Survey(id=10, uuid="s", title="T", description="D")

    q1 = schemas.Question(id=1, question="Q1", survey=mock_survey, answers=[])
    q2 = schemas.Question(id=2, question="Q2", survey=mock_survey, answers=[])
    q3 = schemas.Question(id=3, question="Q3", survey=mock_survey, answers=[])

    answer1 = schemas.Answer(id=1, answer="A1", next_question_id=2)
    answer2 = schemas.Answer(id=2, answer="A2", next_question_id=3)
    answer3 = schemas.Answer(id=3, answer="A3", next_question_id=None)

    pass1 = schemas.Pass(id=1, user_id=1, question_id=1, answer=answer1, question=q1)
    pass2 = schemas.Pass(id=2, user_id=1, question_id=2, answer=answer2, question=q2)
    pass3 = schemas.Pass(id=3, user_id=1, question_id=3, answer=answer3, question=q3)

    mocker.patch.object(engine, "init", new=AsyncMock())
    mocker.patch.object(engine.repository, "survey_by_uuid", return_value=mock_survey)
    mocker.patch.object(
        engine.repository, "user_passes", return_value=[pass2, pass1, pass3]
    )

    result = await engine.get_survey_result("survey-uuid")

    assert result.user == engine.user
    assert len(result.answers) == 3

    assert result.answers[0].id == 1
    assert result.answers[0].next_question_id == 2
    assert result.answers[1].id == 2
    assert result.answers[1].next_question_id == 3
    assert result.answers[2].id == 3
    assert result.answers[2].next_question_id is None


@pytest.mark.asyncio
async def test_get_all_survey_results(mocker, engine):

    user_ids = [1, 2]
    mocker.patch.object(
        engine.repository, "survey_passes_user_id", return_value=user_ids
    )

    mock_result1 = schemas.SurveyResult(user=schemas.User(id=1), answers=[])
    mock_result2 = schemas.SurveyResult(user=schemas.User(id=2), answers=[])

    with patch("survio.main.SurveyEngine") as MockEngine:
        engine1 = AsyncMock()
        engine1.init = AsyncMock()
        engine1.get_survey_result = AsyncMock(return_value=mock_result1)

        engine2 = AsyncMock()
        engine2.init = AsyncMock()
        engine2.get_survey_result = AsyncMock(return_value=mock_result2)

        MockEngine.side_effect = [engine1, engine2]

        result = await engine.get_all_survey_results("survey-uuid")

    assert len(result) == 2
    assert result[0] == mock_result1
    assert result[1] == mock_result2
    engine.repository.survey_passes_user_id.assert_awaited_once_with("survey-uuid")
    engine1.init.assert_awaited_once()
    engine2.init.assert_awaited_once()
    engine1.get_survey_result.assert_awaited_once_with("survey-uuid")
    engine2.get_survey_result.assert_awaited_once_with("survey-uuid")
