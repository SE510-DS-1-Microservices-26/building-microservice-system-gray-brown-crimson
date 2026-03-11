from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_poll_service
from app.core.application.protocol import PollServiceProtocol
from app.core.dto import CreatePollDto


router = APIRouter(prefix="/api/v1/polls", tags=["polls"])

@router.get("/{poll_id}")
def get_poll_by_id(
    poll_id: str,
    service: PollServiceProtocol = Depends(get_poll_service)
):  
    return service.get_poll(poll_id, "1")

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_poll(
    dto: CreatePollDto,
    service: PollServiceProtocol = Depends(get_poll_service)
):
    poll = service.add_new_poll("1", dto)
    
    return poll

@router.put("/{poll_id}")
def update_poll(
    poll_id: str,
    dto: CreatePollDto,
    service: PollServiceProtocol = Depends(get_poll_service)
):
    return service.update_poll(poll_id, "1", dto)

@router.delete("/{poll_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_poll(
    poll_id: str,
    service: PollServiceProtocol = Depends(get_poll_service)    
):
    return service.delete_poll(poll_id, "1")
