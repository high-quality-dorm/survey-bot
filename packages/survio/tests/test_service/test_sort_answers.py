import pytest
from survio.services.survey_service import SurveyService
from survio.schemas import schemas

def create_answer_ext(qid, next_qid, ans_text):
    return schemas.AnswerExt(
        id=1,
        answer=ans_text,
        next_question_id=next_qid,
        question_id=qid,
        question=schemas.Question(
            id=qid,
            question=f"Q{qid}",
            survey=schemas.Survey(id=1, uuid="s", title="T", description="D", first_question_id=1),
            answers=[]
        )
    )

@pytest.fixture
def service():
    return SurveyService()

def test_sort_answers_simple(service):
    ans2 = create_answer_ext(2, 3, "A2")
    ans1 = create_answer_ext(1, 2, "A1")
    ans3 = create_answer_ext(3, None, "A3")
    answers = [ans2, ans1, ans3]
    service._sort_answers(1, answers)
    assert answers[0].question_id == 1
    assert answers[1].question_id == 2
    assert answers[2].question_id == 3

def test_sort_answers_with_skip(service):
    ans1 = create_answer_ext(1, 3, "A1")
    ans3 = create_answer_ext(3, None, "A3")
    answers = [ans3, ans1]
    service._sort_answers(1, answers)
    assert answers[0].question_id == 1
    assert answers[1].question_id == 3

def test_sort_answers_no_first(service):
    ans2 = create_answer_ext(2, None, "A2")
    ans1 = create_answer_ext(1, 2, "A1")
    answers = [ans2, ans1]
    service._sort_answers(99, answers)
    assert answers[0].question_id == 2
    assert answers[1].question_id == 1