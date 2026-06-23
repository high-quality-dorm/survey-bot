from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy import ForeignKey
from survey_service.db.database import Base

class Users(Base):
    __tablename__ = 'users'
    id: int = mapped_column(primary_key=True, autoincrement=True)
    tg_id: int = mapped_column(unique=True)
    name: str = mapped_column()

    passes: list["Passes"] = relationship(back_populates="user")

class Passes(Base):
    __tablename__ = 'passes'
    id: int = mapped_column(primary_key=True, autoincrement=True)
    user_id: int = mapped_column(ForeignKey("users.id"))
    question_id: int = mapped_column(ForeignKey("questions.id"))
    answer_id: int = mapped_column(ForeignKey("answers.id"))

    user: "Users" = relationship(back_populates="passes")
    question: "Questions" = relationship(back_populates="passes")
    answer: "Answers" = relationship(back_populates="passes")

class Answers(Base):
    __tablename__ = "answers"
    id: int = mapped_column(primary_key=True, autoincrement=True)
    question_id: int = mapped_column(ForeignKey("questions.id"))
    next_question_id: int|None = mapped_column(ForeignKey("questions.id"))
    answer: str|None = mapped_column()

    passes: list["Passes"] = relationship(back_populates="answer")
    question: "Questions" = relationship(back_populates="answers",foreign_keys=[question_id])

class Questions(Base):
    __tablename__ = "questions"
    id: int = mapped_column(primary_key=True, autoincrement=True)
    question: str = mapped_column()
    survey_id: int = mapped_column(ForeignKey('surveys.id'))

    passes: list["Passes"] = relationship(back_populates="question")
    answers: list["Answers"] = relationship(back_populates="question",foreign_keys=[Answers.question_id])
    survey: "Surveys" = relationship(back_populates="questions")

class Surveys(Base):
    __tablename__ = "surveys"
    id: int = mapped_column(primary_key=True, autoincrement=True)
    uuid: str = mapped_column(unique=True)
    title: str = mapped_column()
    description: str|None = mapped_column()

    questions: list["Questions"] = relationship(back_populates="survey")
