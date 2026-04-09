from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from src.core_service.app.core.domain import Poll, Question
from src.core_service.app.core.domain.poll_status import PollStatus
from ..models import PollModel, QuestionModel


class PollRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def find_by_id(self, poll_id: UUID, user_id: UUID) -> Poll | None:
        row = self._session.get(PollModel, poll_id)
        if row and row.user_id == user_id:
            return self._to_domain(row)
        return None

    def find_by_id_any_user(self, poll_id: UUID) -> Poll | None:
        row = self._session.get(PollModel, poll_id)
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

    def delete(self, poll_id: UUID, user_id: UUID) -> None:
        row = self._session.get(PollModel, poll_id)
        if row and row.user_id == user_id:
            self._session.delete(row)
            self._session.commit()

    def exists_by_id(self, poll_id: UUID) -> bool:
        return self._session.get(PollModel, poll_id) is not None

    @staticmethod
    def _to_domain(row: PollModel) -> Poll:
        poll = Poll(
            id=row.id,
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
