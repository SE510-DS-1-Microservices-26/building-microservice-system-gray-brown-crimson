import uuid
import pytest
from fastapi.testclient import TestClient

from app.api.main import app
from app.api.dependencies import get_poll_service, get_user_service
from app.core.application.impl.poll_service import PollService
from app.core.application.impl.user_service import UserService
from app.core.domain.poll import Poll
from app.core.domain.user import User


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


@pytest.fixture
def client():
    repo = FakePollRepository()
    user_repo = FakeUserRepository()
    app.dependency_overrides[get_poll_service] = lambda: PollService(repo)
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
        "/api/v1/polls/notexist",
        headers={"x-user-id": "00000000-0000-0000-0000-000000000001"},
    )
    assert response.status_code == 404


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
