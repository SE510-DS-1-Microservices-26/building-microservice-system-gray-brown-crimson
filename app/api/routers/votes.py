from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_vote_service
from app.core.application.protocol import VoteServiceProtocol
from app.core.dto import CreatePollDto


router = APIRouter(prefix="/api/v1/votes", tags=["votes"])

@router.get("/{poll_id}")
def get_vote_by_id(
    poll_id: str,
    service: VoteServiceProtocol = Depends(get_vote_service)
):  
    return service.get_votes(poll_id)
