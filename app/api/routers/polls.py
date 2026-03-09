from fastapi import APIRouter, Depends, status

from app.core.application.poll_service_protocol import PollServiceProtocol
from app.core.application.impl import get_poll_service
from app.core.dto import CreatePollDto

router = APIRouter(prefix="/api/v1/polls", tags=["polls"])


@router.get("/{poll_id}")
def get_poll_by_id(
    poll_id: str,
    service: PollServiceProtocol = Depends(get_poll_service)
):
    poll = service.get_poll(poll_id)
    
    return poll

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_poll(
    dto: CreatePollDto,
    service: PollServiceProtocol = Depends(get_poll_service)
):
    poll = service.add_new_poll("1", dto)
    
    return poll
