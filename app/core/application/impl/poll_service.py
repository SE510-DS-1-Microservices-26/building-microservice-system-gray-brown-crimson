import logging
import uuid

from app.core.application.protocol import PollServiceProtocol
from app.core.domain import Poll, Question
from app.core.dto import CreatePollDto, PollDto
from app.core.mapper import PollMapper
from app.core.exception import PollNotFoundException


logger = logging.getLogger(__name__)

class PollService(PollServiceProtocol):
    def __init__(self):
        self.polls: list[Poll] = []
    
    def get_poll(self, poll_id: str) -> PollDto:
        poll = self._find_poll_or_raise(poll_id)
        
        return PollMapper.to_dto(poll)
    
    def add_new_poll(self, poll_id: str, dto: CreatePollDto) -> PollDto:
        poll = PollMapper.to_domain(dto, poll_id)
        
        self.polls.append(poll)
        
        return PollMapper.to_dto(poll)
    
    def update_poll(self, poll_id: str, dto: CreatePollDto) -> PollDto:
        poll = self._find_poll_or_raise(poll_id)
        
        poll.name = dto.name
        poll.questions = [
            Question(
                id=uuid.uuid4(),
                question=q.question,
                options=q.options
            ) for q in dto.questions
        ]
        
        return PollMapper.to_dto(poll)
        
    def delete_poll(self, poll_id: str) -> None:
        self.polls = [p for p in self.polls if str(p.id) != poll_id]
    
    def _find_poll_or_raise(self, poll_id: str) -> Poll:
        poll = next(
            (u for u in self.polls if poll_id == str(u.id)),
            None
        )
        
        if not poll:
            logger.warning(f"Pol retrieval failed. ID {poll_id} not found in data.")
            raise PollNotFoundException(poll_id)
                
        return poll
