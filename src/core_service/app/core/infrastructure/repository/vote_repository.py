from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from src.core_service.app.core.domain.answer import Answer
from src.core_service.app.core.domain.vote import Vote
from ..models import VoteModel, AnswerModel


class VoteRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, vote: Vote) -> Vote:
        row = VoteModel(
            id=vote.id,
            poll_id=vote.poll_id,
            user_id=vote.user_id,
            created_at=vote.created_at.isoformat(),
            answers=[
                AnswerModel(
                    id=a.id,
                    vote_id=a.vote_id,
                    question_id=a.question_id,
                    selected_option=a.selected_option,
                )
                for a in vote.answers
            ],
        )
        self._session.add(row)
        self._session.commit()
        return vote

    def find_by_poll_and_user(self, poll_id: UUID, user_id: UUID) -> list[Vote]:
        rows = (
            self._session.query(VoteModel)
            .filter(VoteModel.poll_id == poll_id, VoteModel.user_id == user_id)
            .all()
        )
        return [self._to_domain(row) for row in rows]

    @staticmethod
    def _to_domain(row: VoteModel) -> Vote:
        vote = Vote(
            id=row.id,
            poll_id=row.poll_id,
            user_id=row.user_id,
            created_at=datetime.fromisoformat(row.created_at),
        )
        vote.answers = [
            Answer(
                id=a.id,
                vote_id=a.vote_id,
                question_id=a.question_id,
                selected_option=a.selected_option,
            )
            for a in row.answers
        ]
        return vote
