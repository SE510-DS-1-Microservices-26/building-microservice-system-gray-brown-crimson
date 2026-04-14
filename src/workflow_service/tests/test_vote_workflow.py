import uuid
import pytest

from unittest.mock import AsyncMock, Mock

from src.workflow_service.app.core.application.vote_workflow_service import (
    VoteWorkflowService,
)
from src.workflow_service.app.core.domain import (
    WorkflowInstance,
    WorkflowState,
    WorkflowType,
)
from src.workflow_service.app.core.dto import StartVoteWorkflowDto
from src.workflow_service.app.core.dto.start_vote_workflow_dto import AnswerWorkflowDto


class FakeWorkflowRepository:
    def __init__(self):
        self._store = {}

    async def save(self, workflow: WorkflowInstance) -> WorkflowInstance:
        self._store[workflow.workflow_id] = workflow
        return workflow

    async def find_by_id(self, workflow_id: str) -> WorkflowInstance | None:
        return self._store.get(workflow_id)

    async def find_by_poll_and_user(
        self, poll_id: str, user_id: str
    ) -> WorkflowInstance | None:
        for wf in self._store.values():
            if wf.poll_id == poll_id and wf.user_id == user_id:
                return wf
        return None


@pytest.mark.anyio
async def test_vote_workflow_standard_flow():
    poll_client = Mock()
    vote_client = Mock()
    repo = FakeWorkflowRepository()

    poll_client.is_active = AsyncMock(return_value=True)
    vote_client.save_vote = AsyncMock(return_value=str(uuid.uuid4()))
    vote_client.has_user_voted = AsyncMock(return_value=False)

    service = VoteWorkflowService(
        workflow_repo=repo,
        poll_service=poll_client,
        vote_service=vote_client,
    )

    poll_id = uuid.uuid4()
    user_id = uuid.uuid4()
    question_id = uuid.uuid4()

    dto = StartVoteWorkflowDto(
        user_id=user_id,
        poll_id=poll_id,
        answers=[
            AnswerWorkflowDto(question_id=question_id, selected_option="Option A")
        ],
    )

    result = await service.start_vote_workflow(dto)

    assert result.state == WorkflowState.COMPLETED
    assert result.poll_id == str(poll_id)
    assert result.user_id == str(user_id)


@pytest.mark.anyio
async def test_vote_workflow_compensation_after_vote_when_poll_closes():
    poll_client = Mock()
    vote_client = Mock()
    repo = FakeWorkflowRepository()

    poll_client.is_active = AsyncMock(side_effect=[True, False])
    vote_client.has_user_voted = AsyncMock(return_value=False)
    saved_vote_id = str(uuid.uuid4())
    vote_client.save_vote = AsyncMock(return_value=saved_vote_id)
    vote_client.cancel_vote = AsyncMock()

    service = VoteWorkflowService(
        workflow_repo=repo,
        poll_service=poll_client,
        vote_service=vote_client,
    )

    poll_id = uuid.uuid4()
    user_id = uuid.uuid4()
    question_id = uuid.uuid4()

    dto = StartVoteWorkflowDto(
        user_id=user_id,
        poll_id=poll_id,
        answers=[
            AnswerWorkflowDto(question_id=question_id, selected_option="Option A")
        ],
    )

    result = await service.start_vote_workflow(dto)

    assert result.state == WorkflowState.FAILED
    assert result.last_error == "Poll became inactive before workflow completed"
    vote_client.cancel_vote.assert_awaited_once_with(saved_vote_id, str(user_id))


@pytest.mark.anyio
async def test_vote_workflow_save_failure_sets_failed():
    poll_client = Mock()
    vote_client = Mock()
    repo = FakeWorkflowRepository()

    poll_client.is_active = AsyncMock(return_value=True)
    vote_client.has_user_voted = AsyncMock(return_value=False)
    vote_client.save_vote = AsyncMock(side_effect=Exception("Vote Service down"))

    service = VoteWorkflowService(
        workflow_repo=repo,
        poll_service=poll_client,
        vote_service=vote_client,
    )

    poll_id = uuid.uuid4()
    user_id = uuid.uuid4()
    question_id = uuid.uuid4()

    dto = StartVoteWorkflowDto(
        user_id=user_id,
        poll_id=poll_id,
        answers=[
            AnswerWorkflowDto(question_id=question_id, selected_option="Option A")
        ],
    )

    result = await service.start_vote_workflow(dto)

    assert result.state == WorkflowState.FAILED
    assert result.last_error == "Vote Service down"
