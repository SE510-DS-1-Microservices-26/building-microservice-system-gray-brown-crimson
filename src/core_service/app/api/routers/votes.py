from fastapi import APIRouter, Depends

from src.core_service.app.api.dependencies import get_vote_service, get_current_user_id
from src.core_service.app.core.application import VoteService
from src.core_service.app.core.dto import CreateVoteDto


router = APIRouter(prefix="/api/v2/core/votes", tags=["votes"])


@router.get("/{poll_id}")
def get_votes_by_poll_id(
    poll_id: str,
    user_id: str = Depends(get_current_user_id),
    service: VoteService = Depends(get_vote_service),
):
    return service.get_votes(poll_id, user_id)


@router.post("/{poll_id}")
def add_vote(
    poll_id: str,
    payload: CreateVoteDto,
    user_id: str = Depends(get_current_user_id),
    service: VoteService = Depends(get_vote_service),
):
    return service.add_vote(poll_id, user_id, payload)
