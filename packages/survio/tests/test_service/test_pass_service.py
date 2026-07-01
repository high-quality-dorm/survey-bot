import pytest
from survio.services.pass_service import PassService
from survio.db.models import Surveys, Questions, Answers, Passes, Users
from survio.repositories.survey_repository import SurveyRepository
from survio.repositories.question_repository import QuestionRepository
from survio.repositories.answer_repository import AnswerRepository
from survio.repositories.pass_repository import PassRepository
from survio.repositories.user_repository import  UserRepository

@pytest.mark.asyncio
async def test_pass_service_get_with_relationship(session):
    service = PassService()
    user_repo = UserRepository(Users)
    survey_repo = SurveyRepository(Surveys)
    question_repo = QuestionRepository(Questions)
    answer_repo = AnswerRepository(Answers)
    pass_repo = PassRepository(Passes)

    user = Users(id=10)
    await user_repo.create(user, session)
    survey = Surveys(uuid="s1", title="S", first_question_id=0)
    await survey_repo.create(survey, session)
    await session.flush()
    q = Questions(question="Q?", survey_id=survey.id)
    await question_repo.create(q, session)
    await session.flush()
    ans = Answers(question_id=q.id, answer="A", next_question_id=None)
    await answer_repo.create(ans, session)
    await session.flush()
    pass_obj = Passes(user_id=10, question_id=q.id, answer_id=ans.id)
    await pass_repo.create(pass_obj, session)
    await session.flush()
    result = await service.get(pass_obj.id, session)
    assert result is not None
    assert result.user_id == 10
    assert result.answer.answer == "A"

@pytest.mark.asyncio
async def test_pass_service_get_user_passes(session):
    service = PassService()
    user_repo = UserRepository(Users)
    survey_repo = SurveyRepository(Surveys)
    question_repo = QuestionRepository(Questions)
    answer_repo = AnswerRepository(Answers)
    pass_repo = PassRepository(Passes)

    user = Users(id=20)
    await user_repo.create(user, session)
    survey = Surveys(uuid="s2", title="S2", first_question_id=0)
    await survey_repo.create(survey, session)
    await session.flush()
    q1 = Questions(question="Q1", survey_id=survey.id)
    q2 = Questions(question="Q2", survey_id=survey.id)
    await question_repo.create(q1, session)
    await question_repo.create(q2, session)
    await session.flush()
    ans1 = Answers(question_id=q1.id, answer="A1", next_question_id=None)
    ans2 = Answers(question_id=q2.id, answer="A2", next_question_id=None)
    await answer_repo.create(ans1, session)
    await answer_repo.create(ans2, session)
    await session.flush()
    pass1 = Passes(user_id=20, question_id=q1.id, answer_id=ans1.id)
    pass2 = Passes(user_id=20, question_id=q2.id, answer_id=ans2.id)
    await pass_repo.create(pass1, session)
    await pass_repo.create(pass2, session)
    await session.flush()
    passes = await service.get_user_passes(survey.id, 20, session)
    assert len(passes) == 2
    assert passes[0].user_id == 20