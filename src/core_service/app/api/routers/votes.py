from fastapi import APIRouter, Depends, status

from src.core_service.app.api.dependencies import get_vote_service, get_current_user_id
from src.core_service.app.core.application import VoteService
from src.core_service.app.core.dto import CreateVoteDto


router = APIRouter(prefix="/votes", tags=["votes"])


@router.delete("/vote/{vote_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vote(
    vote_id: str,
    user_id: str = Depends(get_current_user_id),
    service: VoteService = Depends(get_vote_service),
):
    return service.cancel_vote(vote_id, user_id)


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


@router.get("/{poll_id}/user/{user_id}")
def has_user_voted(
    poll_id: str,
    user_id: str,
    service: VoteService = Depends(get_vote_service),
):
    return service.has_user_voted(poll_id, user_id)
