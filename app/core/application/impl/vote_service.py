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
        
    def get_votes(self, poll_id: str) -> list[VoteDto]:
        votes = [vote for vote in self.votes if str(vote.poll_id) == poll_id]
        
        return list(map(VoteMapper.to_dto, votes))
