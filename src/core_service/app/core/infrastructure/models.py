import uuid
from datetime import datetime
from uuid import UUID
from sqlalchemy import ForeignKey, Index, String, Text, ARRAY
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


class OutboxMessageModel(Base):
    __tablename__ = "outbox_messages"
    __table_args__ = (Index("ix_outbox_messages_status", "status"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    event_type: Mapped[str] = mapped_column(String(128), nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    routing_key: Mapped[str] = mapped_column(String(128), nullable=False)
    exchange: Mapped[str] = mapped_column(String(128), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="pending")
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, default=datetime.utcnow
    )
    published_at: Mapped[datetime | None] = mapped_column(nullable=True)
