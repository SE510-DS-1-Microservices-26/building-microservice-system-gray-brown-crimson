from fastapi import APIRouter, Depends, status

from app.core.application.user_service_protocol import UserServiceProtocol
from app.core.application.impl import get_user_service


router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(
    payload: dict,
    service: UserServiceProtocol = Depends(get_user_service)
):
    pass
