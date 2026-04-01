from uuid import UUID
from datetime import datetime, UTC

from sqlalchemy.orm import Session

from app.core.domain import Poll, Question
from app.core.domain.poll_status import PollStatus
from app.core.domain.vote import Vote
from .models import PollModel, QuestionModel


class PollRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_short_id(self, short_id: str, user_id: UUID) -> Poll | None:
        row = (
            self._session.query(PollModel)
            .filter(PollModel.short_id == short_id, PollModel.user_id == user_id)
            .first()
        )
        return self._to_domain(row) if row else None

    def save(self, poll: Poll) -> Poll:
        existing = self._session.get(PollModel, poll.id)
        if existing:
            existing.name = poll.name
            existing.status = poll.status.value
            existing.questions = [
                QuestionModel(
                    id=q.id,
                    poll_id=q.poll_id,
                    question=q.question,
                    options=q.options,
                )
                for q in poll.questions
            ]
        else:
            row = PollModel(
                id=poll.id,
                short_id=poll.short_id,
                name=poll.name,
                status=poll.status.value,
                user_id=poll.user_id,
                created_at=poll.created_at.isoformat(),
                questions=[
                    QuestionModel(
                        id=q.id,
                        poll_id=q.poll_id,
                        question=q.question,
                        options=q.options,
                    )
                    for q in poll.questions
                ],
            )
            self._session.add(row)
        self._session.commit()
        return poll

    def delete(self, short_id: str, user_id: UUID) -> None:
        row = (
            self._session.query(PollModel)
            .filter(PollModel.short_id == short_id, PollModel.user_id == user_id)
            .first()
        )
        if row:
            self._session.delete(row)
            self._session.commit()

    def exists_by_short_id(self, short_id: str) -> bool:
        return self._session.query(
            self._session.query(PollModel)
            .filter(PollModel.short_id == short_id)
            .exists()
        ).scalar()

    @staticmethod
    def _to_domain(row: PollModel) -> Poll:
        poll = Poll(
            id=row.id,
            short_id=row.short_id,
            name=row.name,
            status=PollStatus(row.status),
            user_id=row.user_id,
            created_at=datetime.fromisoformat(row.created_at),
        )
        poll.questions = [
            Question(
                id=q.id,
                poll_id=q.poll_id,
                question=q.question,
                options=q.options,
            )
            for q in row.questions
        ]
        return poll
