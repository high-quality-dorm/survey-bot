import pytest
from survio.db.models import Surveys, Questions, Answers, Passes, Users

@pytest.mark.asyncio
async def test_survey_repo_create_and_get_by_uuid(session, survey_repo):
    survey = Surveys(uuid="s1", title="Survey 1", description="Desc", first_question_id=0)
    await survey_repo.create(survey, session)
    await session.flush()
    got = await survey_repo.get_by_uuid("s1", session)
    assert got is not None
    assert got.title == "Survey 1"

@pytest.mark.asyncio
async def test_survey_repo_get_first_question(session, survey_repo, question_repo):
    survey = Surveys(uuid="s2", title="Survey 2", first_question_id=0)
    await survey_repo.create(survey, session)
    await session.flush()
    q = Questions(question="First?", survey_id=survey.id)
    await question_repo.create(q, session)
    await session.flush()
    survey.first_question_id = q.id
    await session.commit()
    first_q = await survey_repo.get_first_question("s2", session)
    assert first_q is not None
    assert first_q.id == q.id
    assert first_q.question == "First?"

@pytest.mark.asyncio
async def test_survey_repo_get_passes_by_uuid(session, survey_repo, question_repo, answer_repo, pass_repo, user_repo):
    survey = Surveys(uuid="s3", title="Survey 3", first_question_id=0)
    await survey_repo.create(survey, session)
    await session.flush()
    q = Questions(question="Q?", survey_id=survey.id)
    await question_repo.create(q, session)
    await session.flush()
    survey.first_question_id = q.id
    await session.commit()
    ans = Answers(question_id=q.id, answer="A", next_question_id=None)
    await answer_repo.create(ans, session)
    await session.flush()
    user = Users(id=10)
    await user_repo.create(user, session)
    await session.flush()
    pass_obj = Passes(user_id=10, question_id=q.id, answer_id=ans.id)
    await pass_repo.create(pass_obj, session)
    await session.commit()
    passes = await survey_repo.get_passes_by_uuid("s3", session)
    assert len(passes) == 1
    assert passes[0].user_id == 10

@pytest.mark.asyncio
async def test_survey_repo_get_survey_passes_user_id(session, survey_repo, question_repo, answer_repo, pass_repo, user_repo):
    survey = Surveys(uuid="s4", title="Survey 4", first_question_id=0)
    await survey_repo.create(survey, session)
    await session.flush()
    q = Questions(question="Q?", survey_id=survey.id)
    await question_repo.create(q, session)
    await session.flush()
    survey.first_question_id = q.id
    await session.commit()
    ans = Answers(question_id=q.id, answer="A", next_question_id=None)
    await answer_repo.create(ans, session)
    await session.flush()
    user1 = Users(id=11)
    user2 = Users(id=12)
    await user_repo.create(user1, session)
    await user_repo.create(user2, session)
    await session.flush()
    pass1 = Passes(user_id=11, question_id=q.id, answer_id=ans.id)
    pass2 = Passes(user_id=12, question_id=q.id, answer_id=ans.id)
    await pass_repo.create(pass1, session)
    await pass_repo.create(pass2, session)
    await session.commit()
    user_ids = await survey_repo.get_survey_passes_user_id(session, "s4")
    assert len(user_ids) == 2
    assert 11 in user_ids and 12 in user_ids