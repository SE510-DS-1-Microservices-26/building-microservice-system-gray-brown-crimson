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
    
    def get_poll(self, poll_id: str, user_id: str) -> PollDto:
        poll = self._find_poll_or_raise(poll_id, user_id)
        
        return PollMapper.to_dto(poll)
    
    def add_new_poll(self, user_id: str, dto: CreatePollDto) -> PollDto:
        poll = PollMapper.to_domain(dto, user_id)
        
        self.polls.append(poll)
        
        return PollMapper.to_dto(poll)
    
    def update_poll(self, poll_id: str, user_id: str, dto: CreatePollDto) -> PollDto:
        poll = self._find_poll_or_raise(poll_id, user_id)
        
        poll.name = dto.name
        poll.questions = [
            Question(
                id=uuid.uuid4(),
                poll_id=uuid.UUID(poll_id),
                question=q.question,
                options=q.options
            ) for q in dto.questions
        ]
        
        return PollMapper.to_dto(poll)
        
    def delete_poll(self, poll_id: str, user_id: str) -> None:
        self.polls = [
            p for p in self.polls 
            if ((str(p.short_id) != poll_id) and (str(p.user_id) != user_id))
        ]
    
    def _find_poll_or_raise(self, poll_id: str, user_id: str) -> Poll:
        poll = next(
            (poll for poll in self.polls if (str(poll.id) == poll_id and str(poll.user_id) == user_id)),
            None
        )
        
        if not poll:
            logger.warning(f"Pol retrieval failed. ID {poll_id} not found in data.")
            raise PollNotFoundException(poll_id)
                
        return poll
    
    def _is_poll_exists(self, poll_id: str) -> bool:
        return any(str(poll.id) == poll_id for poll in self.polls)    
