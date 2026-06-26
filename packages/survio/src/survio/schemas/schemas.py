from pydantic import BaseModel


class Survey(BaseModel):
    id: int
    uuid: str
    title: str
    description: str | None

    model_config = {"from_attributes": True}


class Answer(BaseModel):
    id: int
    answer: str | None
    next_question_id: int | None

    model_config = {"from_attributes": True}


class Question(BaseModel):
    id: int
    question: str
    survey: Survey
    answers: list[Answer]

    model_config = {"from_attributes": True}


class User(BaseModel):
    id: int

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

class AnswerExt(Answer):
    question_id: int
    question: Question

class SurveyResult(BaseModel):
    user: User
    answers: list[AnswerExt]

    model_config = {"from_attributes": True}