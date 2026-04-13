import uuid

from src.core_service.app.core.dto import CreateVoteDto, VoteDto
from src.core_service.app.core.mapper import VoteMapper
from src.core_service.app.core.application.poll_service import PollService
from src.core_service.app.core.application.protocol import (
    VoteRepositoryProtocol,
    UserServiceProtocol,
)
from src.core_service.app.core.exception import UserNotFoundException, VoteNotFoundException


class VoteService:
    def __init__(
        self,
        poll_service: PollService,
        vote_repository: VoteRepositoryProtocol,
        user_client: UserServiceProtocol,
    ):
        self.poll_service = poll_service
        self._vote_repository = vote_repository
        self._user_client = user_client

    def get_votes(self, poll_id: str, user_id: str) -> list[VoteDto]:
        if not self._user_client.user_exists(user_id):
            raise UserNotFoundException(user_id)
        poll = self.poll_service.find_poll(poll_id)
        uid = uuid.UUID(user_id)
        votes = self._vote_repository.find_by_poll_and_user(poll.id, uid)
        return list(map(VoteMapper.to_dto, votes))

    def add_vote(self, poll_id: str, user_id: str, dto: CreateVoteDto) -> VoteDto:
        if not self._user_client.user_exists(user_id):
            raise UserNotFoundException(user_id)
        poll = self.poll_service.find_poll(poll_id)
        vote = VoteMapper.to_domain(dto, poll.id, user_id)
        self._vote_repository.save(vote)
        return VoteMapper.to_dto(vote)

    def has_user_voted(self, poll_id: str, user_id: str) -> bool:
        if not self._user_client.user_exists(user_id):
            raise UserNotFoundException(user_id)
        return self._vote_repository.check_user_voted(
            uuid.UUID(poll_id), uuid.UUID(user_id)
        )

    def cancel_vote(self, vote_id: str, user_id: str) -> None:
        if not self._user_client.user_exists(user_id):
            raise UserNotFoundException(user_id)
        uid = uuid.UUID(user_id)
        vid = uuid.UUID(vote_id)
        vote = self._vote_repository.find_by_id(vid)
        if vote is None or vote.user_id != uid:
            raise VoteNotFoundException(vote_id)
        self._vote_repository.delete(vid)
