from pydantic import BaseModel


class AnswerJSON(BaseModel):
    answer: str | None
    next_question: str | None


class QuestionJSON(BaseModel):
    question: str
    name: str
    answers: list[AnswerJSON]


class SurveyJSON(BaseModel):
    title: str
    description: str | None
    questions: list[QuestionJSON]
