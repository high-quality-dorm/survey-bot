from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from survio.db.database import Base
import uuid


class Users(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    tg_id: Mapped[int] = mapped_column(unique=True)
    name: Mapped[str] = mapped_column()

    passes: Mapped[list["Passes"]] = relationship(back_populates="user")


class Passes(Base):
    __tablename__ = "passes"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    answer_id: Mapped[int] = mapped_column(ForeignKey("answers.id"))

    user: Mapped["Users"] = relationship(back_populates="passes")
    question: Mapped["Questions"] = relationship(back_populates="passes")
    answer: Mapped["Answers"] = relationship(back_populates="passes")


class Answers(Base):
    __tablename__ = "answers"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id"))
    next_question_id: Mapped[int | None] = mapped_column(ForeignKey("questions.id"))
    answer: Mapped[str | None] = mapped_column()

    passes: Mapped[list["Passes"]] = relationship(back_populates="answer")
    question: Mapped["Questions"] = relationship(
        back_populates="answers", foreign_keys=[question_id]
    )


class Questions(Base):
    __tablename__ = "questions"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    question: Mapped[str] = mapped_column()
    survey_id: Mapped[int] = mapped_column(ForeignKey("surveys.id"))

    passes: Mapped[list["Passes"]] = relationship(back_populates="question")
    answers: Mapped[list["Answers"]] = relationship(
        back_populates="question", foreign_keys=[Answers.question_id]
    )
    survey: Mapped["Surveys"] = relationship("Surveys", back_populates="questions")


class Surveys(Base):
    __tablename__ = "surveys"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    uuid: Mapped[str] = mapped_column(unique=True, default=str(uuid.uuid4()))
    title: Mapped[str] = mapped_column()
    first_question_id: Mapped[int] = mapped_column()
    description: Mapped[str | None] = mapped_column()

    questions: Mapped[list["Questions"]] = relationship(back_populates="survey")
