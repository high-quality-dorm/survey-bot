import pytest
from survio.db.models import Questions, Surveys, Answers

@pytest.mark.asyncio
async def test_question_repo_get_with_relationship(session, question_repo, survey_repo):
    survey = Surveys(uuid="q1", title="Survey", first_question_id=0)
    await survey_repo.create(survey, session)
    await session.flush()
    q = Questions(question="Q?", survey_id=survey.id)
    await question_repo.create(q, session)
    await session.flush()
    ans = Answers(question_id=q.id, answer="A", next_question_id=None)
    session.add(ans)
    await session.commit()
    got = await question_repo.get_with_relationship(q.id, session)
    assert got is not None
    assert got.question == "Q?"
    assert got.survey.id == survey.id
    assert len(got.answers) == 1
    assert got.answers[0].answer == "A"