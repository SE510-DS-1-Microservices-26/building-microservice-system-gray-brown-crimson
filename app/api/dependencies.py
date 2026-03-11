from fastapi import Depends

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
