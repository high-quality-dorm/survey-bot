import pytest
from survio.db.models import Passes, Users, Questions, Surveys, Answers

@pytest.mark.asyncio
async def test_pass_repo_get_with_relationship(session, pass_repo, user_repo, survey_repo, question_repo, answer_repo):
    user = Users(id=100)
    await user_repo.create(user, session)
    await session.flush()
    survey = Surveys(uuid="p1", title="Survey", first_question_id=0)
    await survey_repo.create(survey, session)
    await session.flush()
    q = Questions(question="Q?", survey_id=survey.id)
    await question_repo.create(q, session)
    await session.flush()
    ans = Answers(question_id=q.id, answer="A", next_question_id=None)
    await answer_repo.create(ans, session)
    await session.flush()
    pass_obj = Passes(user_id=100, question_id=q.id, answer_id=ans.id)
    await pass_repo.create(pass_obj, session)
    await session.commit()
    got = await pass_repo.get_with_relationship(pass_obj.id, session)
    assert got is not None
    assert got.user.id == 100
    assert got.question.id == q.id
    assert got.answer.id == ans.id

@pytest.mark.asyncio
async def test_pass_repo_get_user_passes(session, pass_repo, user_repo, survey_repo, question_repo, answer_repo):
    user = Users(id=101)
    await user_repo.create(user, session)
    await session.flush()
    survey = Surveys(uuid="p2", title="Survey", first_question_id=0)
    await survey_repo.create(survey, session)
    await session.flush()
    q1 = Questions(question="Q1?", survey_id=survey.id)
    q2 = Questions(question="Q2?", survey_id=survey.id)
    await question_repo.create(q1, session)
    await question_repo.create(q2, session)
    await session.flush()
    ans1 = Answers(question_id=q1.id, answer="A1", next_question_id=None)
    ans2 = Answers(question_id=q2.id, answer="A2", next_question_id=None)
    await answer_repo.create(ans1, session)
    await answer_repo.create(ans2, session)
    await session.flush()
    pass1 = Passes(user_id=101, question_id=q1.id, answer_id=ans1.id)
    pass2 = Passes(user_id=101, question_id=q2.id, answer_id=ans2.id)
    await pass_repo.create(pass1, session)
    await pass_repo.create(pass2, session)
    await session.commit()
    passes = await pass_repo.get_user_passes(survey.id, 101, session)
    assert len(passes) == 2
    q_ids = [p.question_id for p in passes]
    assert q1.id in q_ids and q2.id in q_ids