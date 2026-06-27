from unittest.mock import MagicMock

import pytest

from survio.schemas import json_schemas, schemas


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
    assert result.survey.uuid == "test-uuid"


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

    mock_survey = MagicMock()
    mock_survey.id = 1
    mock_survey.uuid = "uuid"
    mock_survey.title = "Title"
    mock_survey.description = "Desc"

    mock_question = MagicMock()
    mock_question.id = 2
    mock_question.question = "Question?"
    mock_question.survey = mock_survey

    mock_answer = MagicMock()
    mock_answer.id = 3
    mock_answer.answer = "Yes"
    mock_answer.next_question_id = None

    mock_pass = MagicMock()
    mock_pass.id = 1
    mock_pass.user_id = 1
    mock_pass.question_id = 2
    mock_pass.answer = mock_answer
    mock_pass.question = mock_question

    mocker.patch("survio.main.create_pass", return_value=mock_pass)

    result = await survey_repo.answer_question(answer_id=1, user_id=1)

    survey_repo.session.commit.assert_awaited_once()
    assert isinstance(result, schemas.Pass)
    assert result.id == 1
    assert result.question.question == "Question?"
    assert result.answer.answer == "Yes"


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
    mocker.patch("survio.main.create_survey", return_value=mock_survey)

    question_objects = []
    for i, q in enumerate(sample_survey_json["questions"]):
        mock_q = MagicMock()
        mock_q.id = i + 1
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
async def test_survey_by_uuid(mocker, survey_repo):
    mock_survey = MagicMock()
    mock_survey.id = 1
    mock_survey.uuid = "test-uuid"
    mock_survey.title = "Test Survey"
    mock_survey.description = "Test Description"

    mocker.patch("survio.main.get_survey_by_uuid", return_value=mock_survey)

    result = await survey_repo.survey_by_uuid("test-uuid")

    assert isinstance(result, schemas.Survey)
    assert result.uuid == "test-uuid"
    assert result.title == "Test Survey"


@pytest.mark.asyncio
async def test_first_question(mocker, survey_repo):
    mock_survey = MagicMock()
    mock_survey.id = 1
    mock_survey.uuid = "test-uuid"
    mock_survey.title = "Test Survey"
    mock_survey.description = "Test Description"

    mock_question = MagicMock()
    mock_question.id = 1
    mock_question.question = "First question?"
    mock_question.survey = mock_survey
    mock_question.answers = []

    mocker.patch("survio.main.get_first_question", return_value=mock_question)

    result = await survey_repo.first_question("test-uuid")

    assert isinstance(result, schemas.Question)
    assert result.id == 1
    assert result.question == "First question?"
    assert result.survey.uuid == "test-uuid"


@pytest.mark.asyncio
async def test_user_passes(mocker, survey_repo):
    mock_survey = MagicMock()
    mock_survey.id = 1
    mock_survey.uuid = "survey-uuid"
    mock_survey.title = "Survey"
    mock_survey.description = "Desc"

    mock_question = MagicMock()
    mock_question.id = 1
    mock_question.question = "Question?"
    mock_question.survey = mock_survey

    mock_answer = MagicMock()
    mock_answer.id = 1
    mock_answer.answer = "Answer text"
    mock_answer.next_question_id = None

    mock_pass = MagicMock()
    mock_pass.id = 1
    mock_pass.user_id = 1
    mock_pass.question_id = 1
    mock_pass.answer_id = 1
    mock_pass.question = mock_question
    mock_pass.answer = mock_answer

    mocker.patch("survio.main.get_user_passes", return_value=[mock_pass])

    result = await survey_repo.user_passes(survey_id=1, user_id=1)

    assert isinstance(result, list)
    assert len(result) == 1
    pass_schema = result[0]
    assert isinstance(pass_schema, schemas.Pass)
    assert pass_schema.id == 1
    assert pass_schema.answer.answer == "Answer text"
    assert pass_schema.question.question == "Question?"
    assert pass_schema.question.survey.uuid == "survey-uuid"


@pytest.mark.asyncio
async def test_user_passes_empty(mocker, survey_repo):
    mocker.patch("survio.main.get_user_passes", return_value=[])
    result = await survey_repo.user_passes(survey_id=1, user_id=1)
    assert result == []


@pytest.mark.asyncio
async def test_get_passes_by_uuid(mocker, survey_repo):
    mock_survey = MagicMock()
    mock_survey.id = 1
    mock_survey.uuid = "survey-uuid"
    mock_survey.title = "Survey"
    mock_survey.description = "Desc"

    mock_question = MagicMock()
    mock_question.id = 1
    mock_question.question = "Test question?"
    mock_question.survey = mock_survey

    mock_answer = MagicMock()
    mock_answer.id = 1
    mock_answer.answer = "Test answer"
    mock_answer.next_question_id = None

    mock_pass = MagicMock()
    mock_pass.id = 1
    mock_pass.user_id = 1
    mock_pass.question_id = 1
    mock_pass.answer_id = 1
    mock_pass.question = mock_question
    mock_pass.answer = mock_answer

    mocker.patch("survio.main.get_passes_by_uuid", return_value=[mock_pass])

    result = await survey_repo.passes_by_uuid("test-uuid")

    assert isinstance(result, list)
    assert len(result) == 1
    pass_schema = result[0]
    assert pass_schema.id == 1
    assert pass_schema.answer.answer == "Test answer"
    assert pass_schema.question.survey.uuid == "survey-uuid"


@pytest.mark.asyncio
async def test_get_user(mocker, survey_repo):
    mock_user = MagicMock()
    mock_user.id = 1
    mocker.patch("survio.main.get_user", return_value=mock_user)

    result = await survey_repo.get_user(user_id=1)

    assert isinstance(result, schemas.User)
    assert result.id == 1


@pytest.mark.asyncio
async def test_get_user_not_found(mocker, survey_repo):
    mocker.patch("survio.main.get_user", return_value=None)

    result = await survey_repo.get_user(user_id=1)
    assert result is None


@pytest.mark.asyncio
async def test_survey_passes_user_id(mocker, survey_repo):
    expected_ids = [1, 2, 3]
    mocker.patch("survio.main.get_survey_passes_user_id", return_value=expected_ids)

    result = await survey_repo.survey_passes_user_id("test-uuid")

    assert result == expected_ids
