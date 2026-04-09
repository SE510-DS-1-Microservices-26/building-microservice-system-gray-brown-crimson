from fastapi import APIRouter, Depends, status, HTTPException

from src.workflow_service.app.core.dto import StartVoteWorkflowDto, WorkflowDto
from src.workflow_service.app.core.application.vote_workflow_service import VoteWorkflowService
from src.workflow_service.app.api.dependencies import get_vote_workflow_service

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("/vote", status_code=status.HTTP_201_CREATED, response_model=WorkflowDto)
def create_vote(
    dto: StartVoteWorkflowDto,
    service: VoteWorkflowService = Depends(get_vote_workflow_service),
):
    return service.start_vote_workflow(dto)


@router.get("/{workflow_id}", response_model=WorkflowDto)
def get_workflow(
    workflow_id: str,
    service: VoteWorkflowService = Depends(get_vote_workflow_service),
):
    workflow = service.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    return workflow