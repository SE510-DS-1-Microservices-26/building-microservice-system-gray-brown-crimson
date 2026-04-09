import uuid
import pytest

from unittest.mock import Mock

from src.workflow_service.app.core.application.vote_workflow_service import VoteWorkflowService
from src.workflow_service.app.core.domain import WorkflowInstance, WorkflowState, WorkflowType
from src.workflow_service.app.core.dto import StartVoteWorkflowDto
from src.workflow_service.app.core.dto.start_vote_workflow_dto import AnswerWorkflowDto


class FakeWorkflowRepository:
    def __init__(self):
        self._store = {}

    def save(self, workflow: WorkflowInstance) -> WorkflowInstance:
        self._store[workflow.workflow_id] = workflow
        return workflow

    def find_by_id(self, workflow_id: str) -> WorkflowInstance | None:
        return self._store.get(workflow_id)


def test_vote_workflow_standard_flow():
    poll_client = Mock()
    vote_client = Mock()
    repo = FakeWorkflowRepository()
    
    vote_client.save_vote.return_value = str(uuid.uuid4())
    
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
        answers=[AnswerWorkflowDto(question_id=question_id, selected_option="Option A")]
    )

    result = service.start_vote_workflow(dto)
    
    assert result.state == WorkflowState.COMPLETED
    assert result.poll_id == str(poll_id)
    assert result.user_id == str(user_id)


def test_vote_workflow_compensation_flow():
    poll_client = Mock()
    vote_client = Mock()
    repo = FakeWorkflowRepository()
    
    vote_client.save_vote.side_effect = Exception("Vote Service down")
    
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
        answers=[AnswerWorkflowDto(question_id=question_id, selected_option="Option A")]
    )

    result = service.start_vote_workflow(dto)
    
    assert result.state == WorkflowState.FAILED
    assert "Vote Service down" in result.last_error
