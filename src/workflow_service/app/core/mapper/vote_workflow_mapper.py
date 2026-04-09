from datetime import datetime, UTC
from src.workflow_service.app.core.domain import WorkflowInstance, WorkflowType
from src.workflow_service.app.core.dto import StartVoteWorkflowDto, WorkflowDto


class WorkflowMapper:

    @staticmethod
    def from_start_dto(dto: StartVoteWorkflowDto) -> WorkflowInstance:
        return WorkflowInstance(
            type=WorkflowType.VOTE,
            poll_id=str(dto.poll_id),
            user_id=str(dto.user_id),
        )

    @staticmethod
    def to_dto(domain: WorkflowInstance) -> WorkflowDto:
        return WorkflowDto(
            workflow_id=domain.workflow_id,
            type=domain.type,
            state=domain.state,
            poll_id=domain.poll_id,
            user_id=domain.user_id,
            vote_id=domain.vote_id,
            last_error=domain.last_error,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
        )

    @staticmethod
    def advance(
        instance: WorkflowInstance,
        error: str | None = None,
    ) -> WorkflowInstance:
        instance.last_error = error
        instance.updated_at = datetime.now(UTC)
        return instance