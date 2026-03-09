import logging
from app.core.application.poll_service_protocol import PollServiceProtocol
from app.core.domain import Poll
from app.core.dto import CreatePollDto, PollDto
from app.core.mapper import PollMapper
from app.core.exception import PollNotFoundException


logger = logging.getLogger(__name__)

class PollService(PollServiceProtocol):
    def __init__(self):
        self.polls: list[Poll] = []
    
    def get_poll(self, poll_id: str) -> PollDto:
        poll = next(
            (p for p in self.polls if str(p.id) == poll_id),
            None
        )
        
        if not poll:
            logger.warning(f"Poll retrieval failed. ID {poll_id} not found in data.")
            raise PollNotFoundException(poll_id)
        
        return PollMapper.to_dto(poll)
    
    def add_new_poll(self, user_id: str, dto: CreatePollDto) -> PollDto:
        poll = PollMapper.to_domain(dto, user_id)
        
        self.polls.append(poll)
        
        return PollMapper.to_dto(poll)
    
    
def get_poll_service() -> PollServiceProtocol:
    return PollService()
