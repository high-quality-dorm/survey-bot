from pydantic import BaseModel


class Survey(BaseModel):
    uuid: str
    title: str
    description: str | None

    model_config = {"from_attributes": True}


class Answer(BaseModel):
    answer: str | None


class Question(BaseModel):
    question: str
    survey: Survey


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
