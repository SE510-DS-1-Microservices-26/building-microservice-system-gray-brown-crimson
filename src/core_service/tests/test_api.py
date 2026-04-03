import uuid
import pytest
from fastapi.testclient import TestClient

from src.core_service.app.api.main import app
from src.core_service.app.api.dependencies import get_poll_service, get_user_service, get_vote_service
from src.core_service.app.core.application import PollService, VoteService
from users_service.app.core.application.user_service import UserService
from src.core_service.app.core.domain.poll import Poll
from src.users_service.app.core.domain.user import User
from src.core_service.app.core.domain.vote import Vote


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


class FakeUserRepository:
    def __init__(self):
        self._store: dict[uuid.UUID, User] = {}

    def find_by_id(self, user_id: uuid.UUID) -> User | None:
        return self._store.get(user_id)

    def save(self, user: User) -> User:
        self._store[user.id] = user
        return user

    def delete(self, user_id: uuid.UUID) -> None:
        self._store.pop(user_id, None)


class FakeVoteRepository:
    def __init__(self):
        self._store: list[Vote] = []

    def save(self, vote: Vote) -> Vote:
        self._store.append(vote)
        return vote

    def find_by_poll_and_user(self, poll_id: uuid.UUID, user_id: uuid.UUID) -> list[Vote]:
        return [v for v in self._store if v.poll_id == poll_id and v.user_id == user_id]


@pytest.fixture
def client():
    poll_repo = FakePollRepository()
    vote_repo = FakeVoteRepository()
    user_repo = FakeUserRepository()
    poll_service = PollService(poll_repo)
    app.dependency_overrides[get_poll_service] = lambda: poll_service
    app.dependency_overrides[get_vote_service] = lambda: VoteService(poll_service, vote_repo)
    app.dependency_overrides[get_user_service] = lambda: UserService(user_repo)
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health_endpoint_returns_ok(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_poll_returns_201(client):
    response = client.post(
        "/api/v1/polls/",
        json={
            "name": "Favourite Language",
            "questions": [{"question": "Best language?", "options": ["Python", "Java"]}],
        },
        headers={"x-user-id": "00000000-0000-0000-0000-000000000001"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Favourite Language"
    assert data["status"] == "draft"


def test_get_poll_returns_404_for_unknown(client):
    response = client.get(
        f"/api/v1/polls/{uuid.uuid4()}",
        headers={"x-user-id": "00000000-0000-0000-0000-000000000001"},
    )
    assert response.status_code == 404


def test_put_poll_returns_409_when_not_draft(client):
    create_resp = client.post(
        "/api/v1/polls/",
        json={
            "name": "Lock Test",
            "questions": [{"question": "Pick one?", "options": ["A", "B"]}],
        },
        headers={"x-user-id": "00000000-0000-0000-0000-000000000001"},
    )
    poll_id = create_resp.json()["id"]
    client.patch(
        f"/api/v1/polls/{poll_id}/status",
        json={"status": "active"},
        headers={"x-user-id": "00000000-0000-0000-0000-000000000001"},
    )
    put_resp = client.put(
        f"/api/v1/polls/{poll_id}",
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
        "/api/v1/polls/",
        json={
            "name": "Status Test",
            "questions": [{"question": "Pick one?", "options": ["A", "B"]}],
        },
        headers={"x-user-id": "00000000-0000-0000-0000-000000000001"},
    )
    poll_id = create_resp.json()["id"]
    patch_resp = client.patch(
        f"/api/v1/polls/{poll_id}/status",
        json={"status": "active"},
        headers={"x-user-id": "00000000-0000-0000-0000-000000000001"},
    )
    assert patch_resp.status_code == 200
    assert patch_resp.json()["status"] == "active"
