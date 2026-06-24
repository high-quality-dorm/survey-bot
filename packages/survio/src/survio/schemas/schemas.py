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


