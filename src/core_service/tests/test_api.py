import uuid
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.core_service.app.api.main import app
from src.core_service.app.api.dependencies import get_poll_service, get_vote_service
from src.core_service.app.core.application import PollService, VoteService
from src.core_service.app.core.domain.poll import Poll
from src.core_service.app.core.domain.vote import Vote
from src.core_service.app.core.exception import (
    UsersServiceTimeoutException,
    UsersServiceUnavailableException,
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

    def find_by_id(self, vote_id: uuid.UUID) -> Vote | None:
        for v in self._store:
            if v.id == vote_id:
                return v
        return None

    def check_user_voted(self, poll_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        return any(v.poll_id == poll_id and v.user_id == user_id for v in self._store)

    def delete(self, vote_id: uuid.UUID) -> None:
        self._store = [v for v in self._store if v.id != vote_id]


class FakeUserServiceClient:
    def user_exists(self, user_id: str) -> bool:
        return True

    def get_user(self, user_id: str) -> dict:
        return {"id": user_id}


class FakeOutboxRepository:
    def save(self, event) -> None:
        pass


class UnavailableUserServiceClient:
    def user_exists(self, user_id: str) -> bool:
        raise UsersServiceUnavailableException()

    def get_user(self, user_id: str) -> dict:
        raise UsersServiceUnavailableException()


@pytest.fixture
def client():
    poll_repo = FakePollRepository()
    vote_repo = FakeVoteRepository()
    user_client = FakeUserServiceClient()
    outbox_repo = FakeOutboxRepository()
    poll_service = PollService(poll_repo, user_client, outbox_repo)
    app.dependency_overrides[get_poll_service] = lambda: poll_service
    app.dependency_overrides[get_vote_service] = lambda: VoteService(
        poll_service, vote_repo, user_client
    )
    with (
        patch(
            "src.core_service.app.api.main.RabbitMQPublisher", autospec=True
        ) as MockPublisher,
        patch("src.core_service.app.api.main.run_outbox_relay", new_callable=AsyncMock),
    ):
        MockPublisher.return_value.connect = AsyncMock()
        MockPublisher.return_value.close = AsyncMock()
        yield TestClient(app)
    app.dependency_overrides.clear()


def test_health_endpoint_returns_ok(client):
    response = client.get("/api/v2/core/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_poll_returns_201(client):
    response = client.post(
        "/api/v2/core/polls/",
        json={
            "name": "Favourite Language",
            "questions": [
                {"question": "Best language?", "options": ["Python", "Java"]}
            ],
        },
        headers={"x-user-id": "00000000-0000-0000-0000-000000000001"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Favourite Language"
    assert data["status"] == "draft"


def test_get_poll_returns_404_for_unknown(client):
    response = client.get(
        f"/api/v2/core/polls/{uuid.uuid4()}",
        headers={"x-user-id": "00000000-0000-0000-0000-000000000001"},
    )
    assert response.status_code == 404


def test_put_poll_returns_409_when_not_draft(client):
    create_resp = client.post(
        "/api/v2/core/polls/",
        json={
            "name": "Lock Test",
            "questions": [{"question": "Pick one?", "options": ["A", "B"]}],
        },
        headers={"x-user-id": "00000000-0000-0000-0000-000000000001"},
    )
    poll_id = create_resp.json()["id"]
    client.patch(
        f"/api/v2/core/polls/{poll_id}/status",
        json={"status": "active"},
        headers={"x-user-id": "00000000-0000-0000-0000-000000000001"},
    )
    put_resp = client.put(
        f"/api/v2/core/polls/{poll_id}",
        json={
            "name": "Hacked",
            "questions": [{"question": "New Q?", "options": ["X", "Y"]}],
        },
        headers={"x-user-id": "00000000-0000-0000-0000-000000000001"},
    )
    assert put_resp.status_code == 409
    assert put_resp.json()["current_status"] == "active"


def test_patch_poll_status(client):
    create_resp = client.post(
        "/api/v2/core/polls/",
        json={
            "name": "Status Test",
            "questions": [{"question": "Pick one?", "options": ["A", "B"]}],
        },
        headers={"x-user-id": "00000000-0000-0000-0000-000000000001"},
    )
    poll_id = create_resp.json()["id"]
    patch_resp = client.patch(
        f"/api/v2/core/polls/{poll_id}/status",
        json={"status": "active"},
        headers={"x-user-id": "00000000-0000-0000-0000-000000000001"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "active"


def _make_client_with_user_service(raising_user_client):
    poll_repo = FakePollRepository()
    vote_repo = FakeVoteRepository()
    outbox_repo = FakeOutboxRepository()
    poll_service = PollService(poll_repo, raising_user_client, outbox_repo)
    app.dependency_overrides[get_poll_service] = lambda: poll_service
    app.dependency_overrides[get_vote_service] = lambda: VoteService(
        poll_service, vote_repo, raising_user_client
    )


class TimeoutUserServiceClient:
    def user_exists(self, user_id: str) -> bool:
        raise UsersServiceTimeoutException()

    def get_user(self, user_id: str) -> dict:
        raise UsersServiceTimeoutException()


class UnavailableUserServiceClient:
    def user_exists(self, user_id: str) -> bool:
        raise UsersServiceUnavailableException()

    def get_user(self, user_id: str) -> dict:
        raise UsersServiceUnavailableException()


@pytest.fixture
def client_with_timeout_user_service():
    _make_client_with_user_service(TimeoutUserServiceClient())
    with (
        patch(
            "src.core_service.app.api.main.RabbitMQPublisher", autospec=True
        ) as MockPublisher,
        patch("src.core_service.app.api.main.run_outbox_relay", new_callable=AsyncMock),
    ):
        MockPublisher.return_value.connect = AsyncMock()
        MockPublisher.return_value.close = AsyncMock()
        yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def client_with_unavailable_user_service():
    _make_client_with_user_service(UnavailableUserServiceClient())
    with (
        patch(
            "src.core_service.app.api.main.RabbitMQPublisher", autospec=True
        ) as MockPublisher,
        patch("src.core_service.app.api.main.run_outbox_relay", new_callable=AsyncMock),
    ):
        MockPublisher.return_value.connect = AsyncMock()
        MockPublisher.return_value.close = AsyncMock()
        yield TestClient(app)
    app.dependency_overrides.clear()


def test_create_poll_returns_504_when_users_service_times_out(
    client_with_timeout_user_service,
):
    response = client_with_timeout_user_service.post(
        "/api/v2/core/polls/",
        json={
            "name": "Timeout Test",
            "questions": [{"question": "Pick one?", "options": ["A", "B"]}],
        },
        headers={"x-user-id": "00000000-0000-0000-0000-000000000001"},
    )
    assert response.status_code == 504
    assert response.json()["error"] == "Gateway Timeout"


def test_create_poll_returns_503_when_users_service_unavailable(
    client_with_unavailable_user_service,
):
    response = client_with_unavailable_user_service.post(
        "/api/v2/core/polls/",
        json={
            "name": "Unavailable Test",
            "questions": [{"question": "Pick one?", "options": ["A", "B"]}],
        },
        headers={"x-user-id": "00000000-0000-0000-0000-000000000001"},
    )
    assert response.status_code == 503
    body = response.json()
    assert body["error"] == "Service Unavailable"
    assert body["detail"] == "Users service is unreachable."
