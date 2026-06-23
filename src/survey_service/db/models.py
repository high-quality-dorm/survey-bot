from sqlalchemy.orm import mapped_column
from sqlalchemy import ForeignKey, Text
from survey_service.db.database import Base

class Users(Base):
    __tablename__ = 'users'
    id: int = mapped_column(primary_key=True, autoincrement=True)
    tg_id: int = mapped_column(unique=True)
    name: Text

class Passes(Base):
    __tablename__ = 'passes'
    id: int = mapped_column(primary_key=True, autoincrement=True)
    user_id: int = mapped_column(ForeignKey("users.id"))
    question_id: int = mapped_column(ForeignKey("questions.id"))
    answer_id: int = mapped_column(ForeignKey("answers.id"))

class Answers(Base):
    __tablename__ = "answers"
    id: int = mapped_column(primary_key=True, autoincrement=True)
    question_id: int = mapped_column(ForeignKey("questions.id"))
    next_question_id: int|None = mapped_column(ForeignKey("questions.id"))
    answer: Text|None

class Questions(Base):
    __tablename__ = "questions"
    id: int = mapped_column(primary_key=True, autoincrement=True)
    question: Text
    survey_id: int = mapped_column(ForeignKey('surveys.id'))

class Surveys(Base):
    __tablename__ = "surveys"
    id: int = mapped_column(primary_key=True, autoincrement=True)
    uuid: Text = mapped_column(unique=True)
    title: Text
    description: Text|None