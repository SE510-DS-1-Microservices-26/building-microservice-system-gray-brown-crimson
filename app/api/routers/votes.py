from fastapi import APIRouter, Depends

from app.api.dependencies import get_vote_service
from app.core.application.protocol import VoteServiceProtocol
from app.core.dto import CreateVoteDto


router = APIRouter(prefix="/api/v1/votes", tags=["votes"])

@router.get("/{poll_id}")
def get_vote_by_id(
    poll_id: str,
    service: VoteServiceProtocol = Depends(get_vote_service)
):  
    return service.get_votes(poll_id, "1")

@router.post("/{poll_id}")
def add_vote(
    poll_id: str,
    payload: CreateVoteDto,
    service: VoteServiceProtocol = Depends(get_vote_service)
):
    return service.add_vote(poll_id, "1", payload)
