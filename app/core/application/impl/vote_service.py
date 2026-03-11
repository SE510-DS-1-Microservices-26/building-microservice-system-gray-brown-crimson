import logging
from app.core.application.protocol import PollServiceProtocol, VoteServiceProtocol
from app.core.domain import Vote
from app.core.dto import CreateVoteDto, VoteDto
from app.core.mapper import VoteMapper
from app.core.exception import PollNotFoundException


logger = logging.getLogger(__name__)

class VoteService(VoteServiceProtocol):
    def __init__(self, poll_service: PollServiceProtocol):
        self.votes: list[Vote] = []
        self.poll_service = poll_service
        
    def get_votes(self, poll_id: str, user_id: str) -> list[VoteDto]:
        if not self.poll_service._is_poll_exists(poll_id):
            raise PollNotFoundException(poll_id)
        
        votes = [vote for vote in self.votes if ((str(vote.poll_id) == poll_id) and (str(vote.user_id) == user_id))]
        
        return list(map(VoteMapper.to_dto, votes))

    def add_vote(self, poll_id: str, user_id: str, dto: CreateVoteDto) -> VoteDto:
        vote = VoteMapper.to_domain(dto, poll_id, user_id)
        
        self.votes.append(vote)
        
        return VoteMapper.to_dto(vote)
