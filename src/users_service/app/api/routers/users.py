from fastapi import APIRouter, Depends, status

from src.users_service.app.api.dependencies import get_user_service
from src.users_service.app.core.application import UserService
from src.users_service.app.core.dto import CreateUserDto, UpdateUserDto


router = APIRouter(tags=["users"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(
    payload: CreateUserDto, service: UserService = Depends(get_user_service)
):
    return service.add_new_user(payload)


@router.get("/{user_id}")
def get_user_info(user_id: str, service: UserService = Depends(get_user_service)):
    return service.get_user_info(user_id)


@router.put("/{user_id}")
def update_user(
    user_id: str,
    payload: UpdateUserDto,
    service: UserService = Depends(get_user_service),
):
    return service.update_user(user_id, payload)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str, service: UserService = Depends(get_user_service)):
    return service.delete_user(user_id)
