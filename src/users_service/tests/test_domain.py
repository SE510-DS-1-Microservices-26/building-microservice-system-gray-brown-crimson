import uuid
import pytest

from src.users_service.app.core.domain.user import User


def test_user_email_must_contain_at_sign():
    with pytest.raises(ValueError, match="Email must be valid"):
        User(
            id=uuid.uuid4(),
            username="bob",
            firstname="Bob",
            lastname="Smith",
            email="notanemail",
        )


def test_user_username_cannot_be_empty():
    with pytest.raises(ValueError, match="Username cannot be empty"):
        User(
            id=uuid.uuid4(),
            username="",
            firstname="Bob",
            lastname="Smith",
            email="bob@example.com",
        )
