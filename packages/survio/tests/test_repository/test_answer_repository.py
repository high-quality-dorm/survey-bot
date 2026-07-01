import pytest
from survio.db.models import Answers, Questions, Surveys

@pytest.mark.asyncio
async def test_answer_repo_get_with_relationship(session, answer_repo, survey_repo, question_repo):
    survey = Surveys(uuid="a1", title="Survey", first_question_id=0)
    await survey_repo.create(survey, session)
    await session.flush()
    q = Questions(question="Q?", survey_id=survey.id)
    await question_repo.create(q, session)
    await session.flush()
    ans = Answers(question_id=q.id, answer="A", next_question_id=None)
    await answer_repo.create(ans, session)
    await session.flush()
    got = await answer_repo.get_with_relationship(ans.id, session)
    assert got is not None
    assert got.answer == "A"
    assert got.question.id == q.id