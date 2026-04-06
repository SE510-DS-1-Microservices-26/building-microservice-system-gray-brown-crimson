import uuid

import pytest

from src.core_service.app.core.application import PollService, VoteService
from src.core_service.app.core.domain.poll import Poll
from src.core_service.app.core.domain.vote import Vote
from src.core_service.app.core.dto.create_answer_dto import CreateAnswerDto
from src.core_service.app.core.dto.create_poll_dto import CreatePollDto
from src.core_service.app.core.dto.create_question_dto import CreateQuestionDto
from src.core_service.app.core.dto.create_vote_dto import CreateVoteDto
from src.core_service.app.core.exception.poll_not_found_exception import (
    PollNotFoundException,
)


class FakePollRepository:
    def __init__(self):
        self._store: dict[uuid.UUID, Poll] = {}

    def find_by_id(self, poll_id: uuid.UUID, user_id: uuid.UUID) -> Poll | None:
        poll = self._store.get(poll_id)
        if poll and poll.user_id == user_id:
            return poll
        return None

    def find_by_id_any_user(self, poll_id: uuid.UUID) -> Poll | None:
        return self._store.get(poll_id)

    def save(self, poll: Poll) -> Poll:
        self._store[poll.id] = poll
        return poll

    def delete(self, poll_id: uuid.UUID, user_id: uuid.UUID) -> None:
        self._store.pop(poll_id, None)

    def exists_by_id(self, poll_id: uuid.UUID) -> bool:
        return poll_id in self._store


class FakeVoteRepository:
    def __init__(self):
        self._store: list[Vote] = []

    def save(self, vote: Vote) -> Vote:
        self._store.append(vote)
        return vote

    def find_by_poll_and_user(
        self, poll_id: uuid.UUID, user_id: uuid.UUID
    ) -> list[Vote]:
        return [v for v in self._store if v.poll_id == poll_id and v.user_id == user_id]


class FakeUserServiceClient:
    def user_exists(self, user_id: str) -> bool:
        return True

    def get_user(self, user_id: str) -> dict:
        return {"id": user_id}


USER_ID = str(uuid.uuid4())
OTHER_USER_ID = str(uuid.uuid4())


def make_services() -> tuple[PollService, VoteService]:
    poll_repo = FakePollRepository()
    vote_repo = FakeVoteRepository()
    user_client = FakeUserServiceClient()
    poll_service = PollService(poll_repo, user_client)
    vote_service = VoteService(poll_service, vote_repo, user_client)
    return poll_service, vote_service


def create_poll_dto() -> CreatePollDto:
    return CreatePollDto(
        name="Test Poll",
        questions=[CreateQuestionDto(question="Best colour?", options=["Red", "Blue"])],
    )


def vote_dto(poll_dto) -> CreateVoteDto:
    question_id = poll_dto.questions[0].id
    return CreateVoteDto(
        answers=[CreateAnswerDto(question_id=question_id, selected_option="Red")]
    )


def test_add_vote_returns_dto_with_answers():
    poll_service, vote_service = make_services()
    poll = poll_service.add_new_poll(USER_ID, create_poll_dto())
    result = vote_service.add_vote(poll.id, USER_ID, vote_dto(poll))
    assert result.id  # server-generated UUID
    assert len(result.answers) == 1
    assert result.answers[0].selected_option == "Red"


def test_get_votes_returns_saved_votes():
    poll_service, vote_service = make_services()
    poll = poll_service.add_new_poll(USER_ID, create_poll_dto())
    vote_service.add_vote(poll.id, USER_ID, vote_dto(poll))
    votes = vote_service.get_votes(poll.id, USER_ID)
    assert len(votes) == 1


def test_get_votes_returns_empty_for_other_user():
    poll_service, vote_service = make_services()
    poll = poll_service.add_new_poll(USER_ID, create_poll_dto())
    vote_service.add_vote(poll.id, USER_ID, vote_dto(poll))
    other_votes = vote_service.get_votes(poll.id, OTHER_USER_ID)
    assert other_votes == []


def test_add_vote_raises_for_unknown_poll():
    poll_service, vote_service = make_services()
    dummy_dto = CreateVoteDto(
        answers=[CreateAnswerDto(question_id=uuid.uuid4(), selected_option="X")]
    )
    with pytest.raises(PollNotFoundException):
        vote_service.add_vote(str(uuid.uuid4()), USER_ID, dummy_dto)


def test_multiple_votes_stored_independently():
    poll_service, vote_service = make_services()
    poll = poll_service.add_new_poll(USER_ID, create_poll_dto())
    vote_service.add_vote(poll.id, USER_ID, vote_dto(poll))
    vote_service.add_vote(poll.id, USER_ID, vote_dto(poll))
    votes = vote_service.get_votes(poll.id, USER_ID)
    assert len(votes) == 2
