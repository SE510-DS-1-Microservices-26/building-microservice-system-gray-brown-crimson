from fastapi import APIRouter, Depends

from app.api.dependencies import get_vote_service, get_current_user_id
from app.core.application.protocol import VoteServiceProtocol
from app.core.dto import CreateVoteDto


router = APIRouter(prefix="/api/v1/votes", tags=["votes"])

@router.get("/{poll_id}")
def get_vote_by_id(
    poll_id: str,
    user_id: str = Depends(get_current_user_id),
    service: VoteServiceProtocol = Depends(get_vote_service),
):
    return service.get_votes(poll_id, user_id)

@router.post("/{poll_id}")
def add_vote(
    poll_id: str,
    payload: CreateVoteDto,
    user_id: str = Depends(get_current_user_id),
    service: VoteServiceProtocol = Depends(get_vote_service),
):
    return service.add_vote(poll_id, user_id, payload)
