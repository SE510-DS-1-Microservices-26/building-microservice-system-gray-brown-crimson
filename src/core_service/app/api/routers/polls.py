from fastapi import APIRouter, Depends, status

from src.core_service.app.api.dependencies import get_current_user_id, get_poll_service
from src.core_service.app.core.application import PollService
from src.core_service.app.core.dto import CreatePollDto, UpdatePollStatusDto


router = APIRouter(prefix="/polls", tags=["polls"])


@router.get("/{poll_id}")
def get_poll_by_id(
    poll_id: str,
    user_id: str = Depends(get_current_user_id),
    service: PollService = Depends(get_poll_service),
):
    return service.get_poll(poll_id, user_id)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_poll(
    dto: CreatePollDto,
    user_id: str = Depends(get_current_user_id),
    service: PollService = Depends(get_poll_service),
):
    return service.add_new_poll(user_id, dto)


@router.patch("/{poll_id}/status")
def update_poll_status(
    poll_id: str,
    dto: UpdatePollStatusDto,
    user_id: str = Depends(get_current_user_id),
    service: PollService = Depends(get_poll_service),
):
    return service.update_poll_status(poll_id, user_id, dto)


@router.put("/{poll_id}")
def update_poll(
    poll_id: str,
    dto: CreatePollDto,
    user_id: str = Depends(get_current_user_id),
    service: PollService = Depends(get_poll_service),
):
    return service.update_poll(poll_id, user_id, dto)


@router.delete("/{poll_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_poll(
    poll_id: str,
    user_id: str = Depends(get_current_user_id),
    service: PollService = Depends(get_poll_service),
):
    return service.delete_poll(poll_id, user_id)
