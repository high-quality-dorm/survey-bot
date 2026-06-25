import pytest
from unittest.mock import MagicMock
from survio.schemas import schemas, json_schemas


@pytest.mark.asyncio
async def test_get_question_with_answers(mocker, survey_repo):
    mock_survey = MagicMock()
    mock_survey.id = 1
    mock_survey.uuid = "test-uuid"
    mock_survey.title = "Test Survey"
    mock_survey.description = "Test Description"

    mock_question = MagicMock()
    mock_question.id = 1
    mock_question.question = "Test Question"
    mock_question.survey = mock_survey
    mock_question.answers = []

    mocker.patch("survio.main.get_question", return_value=mock_question)

    result = await survey_repo.get_question_with_answers(question_id=1)
    assert isinstance(result, schemas.Question)
    assert result.id == 1
    assert result.question == "Test Question"
    assert result.survey.title == "Test Survey"


@pytest.mark.asyncio
async def test_create_user(mocker, survey_repo):
    mock_user = MagicMock()
    mock_user.id = 1
    mocker.patch("survio.main.create_user", return_value=mock_user)

    result = await survey_repo.create_user(id=1)
    survey_repo.session.commit.assert_awaited_once()
    assert isinstance(result, schemas.User)
    assert result.id == 1


@pytest.mark.asyncio
async def test_answer_question(mocker, survey_repo):
    mock_pass = MagicMock()
    mock_pass.id = 1
    mock_pass.user_id = 1
    mock_pass.question_id = 2
    mock_pass.answer = MagicMock(id=3, answer="Yes", next_question_id=None)

    mocker.patch("survio.main.create_pass", return_value=mock_pass)

    result = await survey_repo.answer_question(answer_id=1, user_id=1)
    survey_repo.session.commit.assert_awaited_once()
    assert isinstance(result, schemas.Pass)
    assert result.id == 1


@pytest.mark.asyncio
async def test_answer_and_get_next_question_with_next(mocker, survey_repo):
    mock_pass = MagicMock()
    mock_pass.id = 1
    mock_pass.answer = MagicMock(next_question_id=5)
    mocker.patch.object(survey_repo, "answer_question", return_value=mock_pass)

    mock_survey = MagicMock()
    mock_survey.id = 2
    mock_survey.uuid = "next-uuid"
    mock_survey.title = "Next Survey"
    mock_survey.description = "Next Description"

    mock_question = MagicMock()
    mock_question.id = 5
    mock_question.question = "Next question"
    mock_question.survey = mock_survey
    mock_question.answers = []

    mocker.patch("survio.main.get_question", return_value=mock_question)

    result = await survey_repo.answer_and_get_next_question(answer_id=1, user_id=1)
    assert isinstance(result, schemas.Question)
    assert result.id == 5
    assert result.question == "Next question"
    assert result.survey.uuid == "next-uuid"


@pytest.mark.asyncio
async def test_answer_and_get_next_question_no_next(mocker, survey_repo):
    mock_pass = MagicMock()
    mock_pass.answer = MagicMock(next_question_id=None)
    mocker.patch.object(survey_repo, "answer_question", return_value=mock_pass)

    result = await survey_repo.answer_and_get_next_question(answer_id=1, user_id=1)
    assert result is None


@pytest.mark.asyncio
async def test_create_survey_in_db(mocker, survey_repo, sample_survey_json):
    mock_survey = MagicMock()
    mock_survey.id = 10
    mock_survey.uuid = "generated-uuid"
    mock_survey.first_question_id = 0

    async def create_survey_side_effect(session, title, description):
        return mock_survey

    mocker.patch("survio.main.create_survey", side_effect=create_survey_side_effect)

    question_ids = [1, 2]
    question_objects = []
    for i, q in enumerate(sample_survey_json["questions"]):
        mock_q = MagicMock()
        mock_q.id = question_ids[i]
        mock_q.question = q["question"]
        mock_q.survey_id = 10
        question_objects.append(mock_q)

    create_question_mock = mocker.patch("survio.main.create_question")
    create_question_mock.side_effect = question_objects

    create_answer_mock = mocker.patch(
        "survio.main.create_answer", return_value=MagicMock()
    )

    survey_data = json_schemas.SurveyJSON(**sample_survey_json)

    uuid_result = await survey_repo.create_survey_in_db(survey_data)

    survey_repo.session.commit.assert_awaited_once()

    assert create_question_mock.call_count == 2

    assert create_answer_mock.call_count == 4

    assert mock_survey.first_question_id == 1

    assert uuid_result == "generated-uuid"


@pytest.mark.asyncio
async def test_parse_and_create_survey_from_path(
    mocker, survey_repo, tmp_path, sample_survey_json
):
    file_path = tmp_path / "survey.json"
    import json

    with open(file_path, "w") as f:
        json.dump(sample_survey_json, f)

    mocker.patch.object(survey_repo, "create_survey_in_db", return_value="uuid-123")

    result = await survey_repo.parse_and_create_survey(file_path)
    survey_repo.create_survey_in_db.assert_awaited_once()
    assert result == "uuid-123"


@pytest.mark.asyncio
async def test_parse_and_create_survey_from_str(
    mocker, survey_repo, sample_survey_json
):
    import json

    json_str = json.dumps(sample_survey_json)

    mocker.patch.object(survey_repo, "create_survey_in_db", return_value="uuid-456")

    result = await survey_repo.parse_and_create_survey(json_str)
    survey_repo.create_survey_in_db.assert_awaited_once()
    assert result == "uuid-456"
