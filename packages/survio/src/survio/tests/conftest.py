import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from survio.main import SurveyRepository


@pytest.fixture
def mock_session():
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.flush = AsyncMock()
    session.add = MagicMock()
    return session


@pytest.fixture
def survey_repo(mock_session):
    return SurveyRepository(session=mock_session)


@pytest.fixture
def sample_survey_json():
    return {
        "title": "Test Survey",
        "description": "Test Description",
        "questions": [
            {
                "name": "q1",
                "question": "What is your name?",
                "answers": [
                    {"answer": "John", "next_question": "q2"},
                    {"answer": "Jane", "next_question": None},
                ],
            },
            {
                "name": "q2",
                "question": "How old are you?",
                "answers": [
                    {"answer": "20", "next_question": None},
                    {"answer": "30", "next_question": None},
                ],
            },
        ],
    }
