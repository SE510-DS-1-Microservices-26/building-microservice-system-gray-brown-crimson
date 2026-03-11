from fastapi import Depends, Header

from app.core.application.protocol import PollServiceProtocol, VoteServiceProtocol, UserServiceProtocol
from app.core.application.impl import PollService, VoteService, UserService


def get_poll_service() -> PollServiceProtocol:
    return PollService()

def get_vote_service(
        poll_service: PollServiceProtocol = Depends(get_poll_service)
    ) -> VoteServiceProtocol:
    return VoteService(poll_service)

def get_user_service() -> UserServiceProtocol:
    return UserService()

def get_current_user_id(x_user_id: str = Header(default="00000000-0000-0000-0000-000000000001")) -> str:
    return x_user_id
