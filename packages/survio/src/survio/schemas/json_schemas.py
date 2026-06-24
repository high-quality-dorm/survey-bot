from pydantic import BaseModel
from survio.schemas.schemas import Answer


class AnswerJSON(Answer):
    next_question: str | None


class QuestionJSON(BaseModel):
    question: str
    name: str
    answers: list[AnswerJSON]


class SurveyJSON(BaseModel):
    title: str
    description: str | None
    questions: list[QuestionJSON]
