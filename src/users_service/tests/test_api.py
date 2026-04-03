import uuid
import pytest
from fastapi.testclient import TestClient

from src.core_service.app.api.main import app
from src.users_service.app.api.dependencies import get_user_service
from src.users_service.app.core.application.user_service import UserService
from src.users_service.app.core.domain.user import User


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
    user_repo = FakeUserRepository()
    app.dependency_overrides[get_user_service] = lambda: UserService(user_repo)
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health_endpoint_returns_ok(client):
    response = client.get("/api/v2/users/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
