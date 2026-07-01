import pytest
import pytest_asyncio
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from survio.db.database import Base
from survio.db.models import (
    Surveys, Questions, Answers, Passes, Users
)
from survio.repositories.survey_repository import SurveyRepository
from survio.repositories.question_repository import QuestionRepository
from survio.repositories.answer_repository import AnswerRepository
from survio.repositories.pass_repository import PassRepository
from survio.repositories.user_repository import  UserRepository
from survio.main import SurveyEngine

TEST_DATABASE_URL = "sqlite+aiosqlite:///database.db"

@pytest.fixture(scope="session")
def engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False, poolclass=NullPool)
    return engine

@pytest_asyncio.fixture(scope="session", autouse=True)
async def create_tables(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def session(engine):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session_maker() as session:
        yield session
        await session.rollback()
        async with engine.begin() as conn:
            for table in reversed(Base.metadata.sorted_tables):
                await conn.execute(delete(table))
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
def survey_engine(session):
    return SurveyEngine(user_id=1, session=session)

@pytest.fixture
def survey_repo():
    return SurveyRepository(Surveys)

@pytest.fixture
def question_repo():
    return QuestionRepository(Questions)

@pytest.fixture
def answer_repo():
    return AnswerRepository(Answers)

@pytest.fixture
def pass_repo():
    return PassRepository(Passes)

@pytest.fixture
def user_repo():
    return UserRepository(Users)

@pytest.fixture
def sample_survey_json():
    return {
        "title": "Test Survey",
        "description": "Desc",
        "questions": [
            {
                "name": "q1",
                "question": "First question?",
                "answers": [
                    {"answer": "Yes", "next_question": "q2"},
                    {"answer": "No", "next_question": None}
                ]
            },
            {
                "name": "q2",
                "question": "Second question?",
                "answers": [{"answer": "Ok", "next_question": None}]
            }
        ]
    }