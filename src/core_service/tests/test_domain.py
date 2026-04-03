import uuid
import pytest

from src.core_service.app.core.domain.poll import Poll
from src.core_service.app.core.domain.poll_status import PollStatus
from src.core_service.app.core.domain.question import Question
from src.users_service.app.core.domain.user import User


def make_poll(**kwargs) -> Poll:
    defaults = dict(name="My Poll", user_id=uuid.uuid4())
    return Poll(**{**defaults, **kwargs})


def make_question(**kwargs) -> Question:
    defaults = dict(id=uuid.uuid4(), poll_id=uuid.uuid4(), question="Favourite colour?", options=["Red", "Blue"])
    return Question(**{**defaults, **kwargs})


# --- Domain rule 1: Poll name cannot be empty ---

def test_poll_name_cannot_be_empty():
    with pytest.raises(ValueError, match="Poll name cannot be empty"):
        make_poll(name="")


def test_poll_name_whitespace_only_is_rejected():
    with pytest.raises(ValueError, match="Poll name cannot be empty"):
        make_poll(name="   ")


# --- Domain rule 2: Status transitions are limited ---

def test_poll_draft_can_transition_to_active():
    poll = make_poll()
    poll.change_status(PollStatus.ACTIVE)
    assert poll.status == PollStatus.ACTIVE


def test_poll_active_can_transition_to_completed():
    poll = make_poll()
    poll.change_status(PollStatus.ACTIVE)
    poll.change_status(PollStatus.COMPLETED)
    assert poll.status == PollStatus.COMPLETED


def test_poll_cannot_skip_from_draft_to_completed():
    poll = make_poll()
    with pytest.raises(ValueError, match="Cannot transition poll"):
        poll.change_status(PollStatus.COMPLETED)


def test_poll_completed_cannot_transition_anywhere():
    poll = make_poll()
    poll.change_status(PollStatus.ACTIVE)
    poll.change_status(PollStatus.COMPLETED)
    with pytest.raises(ValueError, match="Cannot transition poll"):
        poll.change_status(PollStatus.DRAFT)


# --- Domain rule 3: Question requires at least 2 options ---

def test_question_requires_at_least_two_options():
    with pytest.raises(ValueError, match="at least 2 options"):
        make_question(options=["Only one"])


def test_question_text_cannot_be_empty():
    with pytest.raises(ValueError, match="Question text cannot be empty"):
        make_question(question="")


# --- Domain rule 4: Questions cannot be added to non-DRAFT polls ---

def test_cannot_add_question_to_active_poll():
    poll = make_poll()
    poll.change_status(PollStatus.ACTIVE)
    q = make_question(poll_id=poll.id)
    with pytest.raises(ValueError, match="DRAFT"):
        poll.add_question(q)


# --- Domain rule 5: User email must be valid ---

def test_user_email_must_contain_at_sign():
    with pytest.raises(ValueError, match="Email must be valid"):
        User(id=uuid.uuid4(), username="bob", firstname="Bob", lastname="Smith", email="notanemail")


def test_user_username_cannot_be_empty():
    with pytest.raises(ValueError, match="Username cannot be empty"):
        User(id=uuid.uuid4(), username="", firstname="Bob", lastname="Smith", email="bob@example.com")
