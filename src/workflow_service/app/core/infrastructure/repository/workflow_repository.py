from sqlalchemy import select
import uuid

from sqlalchemy.ext.asyncio.session import AsyncSession

from src.workflow_service.app.core.application.protocol.workflow_repository_protocol import WorkflowRepositoryProtocol
from src.workflow_service.app.core.domain import WorkflowInstance, WorkflowState, WorkflowType
from src.workflow_service.app.core.infrastructure.models import WorkflowInstanceModel


class WorkflowRepository(WorkflowRepositoryProtocol):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
    
    async def save(self, workflow: WorkflowInstance) -> WorkflowInstance:
        model = WorkflowInstanceModel(
            workflow_id=uuid.UUID(workflow.workflow_id),
            type=workflow.type.value if isinstance(workflow.type, WorkflowType) else workflow.type,
            state=workflow.state.value if isinstance(workflow.state, WorkflowState) else workflow.state,
            poll_id=workflow.poll_id,
            user_id=workflow.user_id,
            vote_id=workflow.vote_id,
            last_error=workflow.last_error,
            created_at=workflow.created_at,
            updated_at=workflow.updated_at,
        )
        await self._session.merge(model)
        await self._session.flush()
        return workflow

    async def find_by_id(self, workflow_id: str) -> WorkflowInstance | None:
        result = await self._session.execute(
            select(WorkflowInstanceModel).filter_by(workflow_id=uuid.UUID(workflow_id))
        )

        model = result.scalars().first()

        if not model:
            return None

        return WorkflowInstance(
            workflow_id=str(model.workflow_id),
            type=WorkflowType(model.type),
            state=WorkflowState(model.state),
            poll_id=model.poll_id,
            user_id=model.user_id,
            vote_id=model.vote_id,
            last_error=model.last_error,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def find_by_poll_and_user(self, poll_id: str, user_id: str) -> WorkflowInstance | None:
        result = await self._session.execute(
            select(WorkflowInstanceModel).filter_by(poll_id=poll_id, user_id=user_id, type=WorkflowType.VOTE.value)
        )

        model = result.scalars().first()

        if not model:
            return None

        return WorkflowInstance(
            workflow_id=str(model.workflow_id),
            type=WorkflowType(model.type),
            state=WorkflowState(model.state),
            poll_id=model.poll_id,
            user_id=model.user_id,
            vote_id=model.vote_id,
            last_error=model.last_error,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
        