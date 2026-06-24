from pydantic import BaseModel


class Survey(BaseModel):
    uuid: str
    title: str
    description: str | None

    model_config = {"from_attributes": True}


class Answer(BaseModel):
    answer: str | None
    next_question_id: int | None

    model_config = {"from_attributes": True}


class Question(BaseModel):
    question: str
    survey: Survey
    answers: list[Answer]

    model_config = {"from_attributes": True}
