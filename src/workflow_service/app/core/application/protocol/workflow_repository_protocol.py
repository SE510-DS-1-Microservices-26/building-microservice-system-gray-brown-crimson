from typing import Protocol

from src.workflow_service.app.core.domain import WorkflowInstance


class WorkflowRepositoryProtocol(Protocol):
    async def save(self, workflow: WorkflowInstance) -> WorkflowInstance: ...

    async def find_by_id(self, workflow_id: str) -> WorkflowInstance | None: ...

    async def find_by_poll_and_user(
        self, poll_id: str, user_id: str
    ) -> WorkflowInstance | None: ...
