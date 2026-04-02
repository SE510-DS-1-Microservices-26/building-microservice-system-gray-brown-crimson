from uuid import UUID
from sqlalchemy import ForeignKey, String, ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class PollModel(Base):
    __tablename__ = "polls"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="draft")
    user_id: Mapped[UUID] = mapped_column(nullable=False)
    created_at: Mapped[str] = mapped_column(nullable=False)

    questions: Mapped[list["QuestionModel"]] = relationship(
        back_populates="poll", cascade="all, delete-orphan"
    )
    votes: Mapped[list["VoteModel"]] = relationship(
        back_populates="poll", cascade="all, delete-orphan"
    )


class QuestionModel(Base):
    __tablename__ = "questions"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    poll_id: Mapped[UUID] = mapped_column(ForeignKey("polls.id"), nullable=False)
    question: Mapped[str] = mapped_column(String(512), nullable=False)
    options: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)

    poll: Mapped["PollModel"] = relationship(back_populates="questions")


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    firstname: Mapped[str] = mapped_column(String(128), nullable=False)
    lastname: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    created_at: Mapped[str] = mapped_column(nullable=False)


class VoteModel(Base):
    __tablename__ = "votes"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    poll_id: Mapped[UUID] = mapped_column(ForeignKey("polls.id"), nullable=False)
    user_id: Mapped[UUID] = mapped_column(nullable=False)
    created_at: Mapped[str] = mapped_column(nullable=False)

    poll: Mapped["PollModel"] = relationship(back_populates="votes")
    answers: Mapped[list["AnswerModel"]] = relationship(
        back_populates="vote", cascade="all, delete-orphan"
    )


class AnswerModel(Base):
    __tablename__ = "answers"

    id: Mapped[UUID] = mapped_column(primary_key=True)
    vote_id: Mapped[UUID] = mapped_column(ForeignKey("votes.id"), nullable=False)
    question_id: Mapped[UUID] = mapped_column(nullable=False)
    selected_option: Mapped[str] = mapped_column(String(512), nullable=False)

    vote: Mapped["VoteModel"] = relationship(back_populates="answers")
