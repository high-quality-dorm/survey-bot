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

class User(BaseModel):
    id: int
    tg_id: int
    name: str

    model_config = {"from_attributes": True}


class Pass(BaseModel):
    id: int
    user_id: int
    question_id: int
    answer: Answer

    model_config = {"from_attributes": True}


class UserPass(User):
    passes: Pass
    
    model_config = {"from_attributes": True}

