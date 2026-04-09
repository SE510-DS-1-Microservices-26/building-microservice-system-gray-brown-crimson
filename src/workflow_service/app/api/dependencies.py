import os
from typing import AsyncGenerator

from fastapi import Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.workflow_service.app.core.application.vote_workflow_service import (
    VoteWorkflowService,
)
from src.workflow_service.app.core.infrastructure.client.poll_service_client import (
    PollService,
)
from src.workflow_service.app.core.infrastructure.client.vote_service_client import (
    VoteService,
)
from src.workflow_service.app.core.infrastructure.repository.workflow_repository import (
    WorkflowRepository,
)
from src.workflow_service.app.core.infrastructure.database import AsyncSessionLocal


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


def get_vote_workflow_service(
    request: Request, session: AsyncSession = Depends(get_db_session)
) -> VoteWorkflowService:
    shared_http_client = request.state.http_client

    poll_client = PollService(
        base_url=os.getenv("POLL_SERVICE_URL", "http://core_service:8000/api/v2/core"),
        client=shared_http_client,
    )
    vote_client = VoteService(
        base_url=os.getenv("VOTE_SERVICE_URL", "http://core_service:8000/api/v2/core"),
        client=shared_http_client,
    )

    workflow_repo = WorkflowRepository(session)

    return VoteWorkflowService(
        workflow_repo=workflow_repo,
        poll_service=poll_client,
        vote_service=vote_client,
    )
