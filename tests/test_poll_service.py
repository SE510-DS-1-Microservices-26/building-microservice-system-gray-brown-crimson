import uuid
import pytest

from app.core.application.impl.poll_service import PollService
from app.core.domain.poll import Poll
from app.core.domain.poll_status import PollStatus
from app.core.dto.create_poll_dto import CreatePollDto
from app.core.dto.create_question_dto import CreateQuestionDto
from app.core.dto.update_poll_status_dto import UpdatePollStatusDto
from app.core.exception.poll_not_found_exception import PollNotFoundException


class FakePollRepository:
    def __init__(self):
        self._store: dict[str, Poll] = {}

    def find_by_short_id(self, short_id: str, user_id: uuid.UUID) -> Poll | None:
        poll = self._store.get(short_id)
        if poll and poll.user_id == user_id:
            return poll
        return None

    def save(self, poll: Poll) -> Poll:
        self._store[poll.short_id] = poll
        return poll

    def delete(self, short_id: str, user_id: uuid.UUID) -> None:
        self._store.pop(short_id, None)

    def exists_by_short_id(self, short_id: str) -> bool:
        return short_id in self._store


USER_ID = str(uuid.uuid4())


def make_service() -> PollService:
    return PollService(FakePollRepository())


def create_dto(name: str = "Test Poll") -> CreatePollDto:
    return CreatePollDto(
        name=name,
        questions=[CreateQuestionDto(question="Best colour?", options=["Red", "Blue"])]
    )


def test_add_new_poll_returns_dto_with_correct_name():
    service = make_service()
    result = service.add_new_poll(USER_ID, create_dto("My Poll"))
    assert result.name == "My Poll"


def test_add_new_poll_starts_in_draft_status():
    service = make_service()
    result = service.add_new_poll(USER_ID, create_dto())
    assert result.status == PollStatus.DRAFT


def test_get_poll_raises_not_found_for_unknown_id():
    service = make_service()
    with pytest.raises(PollNotFoundException):
        service.get_poll("nonexistent", USER_ID)


def test_update_poll_status_transitions_to_active():
    service = make_service()
    poll_dto = service.add_new_poll(USER_ID, create_dto())
    updated = service.update_poll_status(
        poll_dto.id, USER_ID, UpdatePollStatusDto(status=PollStatus.ACTIVE)
    )
    assert updated.status == PollStatus.ACTIVE


def test_update_poll_status_invalid_transition_raises():
    from app.core.exception.poll_not_found_exception import PollNotFoundException
    service = make_service()
    poll_dto = service.add_new_poll(USER_ID, create_dto())
    with pytest.raises(ValueError, match="Cannot transition poll"):
        service.update_poll_status(
            poll_dto.id, USER_ID, UpdatePollStatusDto(status=PollStatus.COMPLETED)
        )
