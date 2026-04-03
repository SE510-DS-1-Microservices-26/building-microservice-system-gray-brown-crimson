import logging
import uuid

from src.core_service.app.core.domain import Poll, Question
from src.core_service.app.core.dto import CreatePollDto, PollDto, UpdatePollStatusDto
from src.core_service.app.core.mapper import PollMapper
from src.core_service.app.core.exception import PollNotFoundException, PollNotEditableException
from src.core_service.app.core.application.protocol import PollRepositoryProtocol


logger = logging.getLogger(__name__)


class PollService:
    def __init__(self, repository: PollRepositoryProtocol):
        self._repository = repository

    def get_poll(self, poll_id: str, user_id: str) -> PollDto:
        poll = self._find_poll_or_raise(poll_id, user_id)
        return PollMapper.to_dto(poll)

    def add_new_poll(self, user_id: str, dto: CreatePollDto) -> PollDto:
        poll = PollMapper.to_domain(dto, user_id)
        self._repository.save(poll)
        return PollMapper.to_dto(poll)

    def update_poll(self, poll_id: str, user_id: str, dto: CreatePollDto) -> PollDto:
        poll = self._find_poll_or_raise(poll_id, user_id)
        poll.name = dto.name
        new_questions = [
            Question(
                id=uuid.uuid4(),
                poll_id=poll.id,
                question=q.question,
                options=q.options,
            )
            for q in dto.questions
        ]
        try:
            poll.set_questions(new_questions)
        except ValueError as exc:
            raise PollNotEditableException(poll_id, poll.status.value) from exc
        self._repository.save(poll)
        return PollMapper.to_dto(poll)

    def update_poll_status(self, poll_id: str, user_id: str, dto: UpdatePollStatusDto) -> PollDto:
        poll = self._find_poll_or_raise(poll_id, user_id)
        poll.change_status(dto.status)
        self._repository.save(poll)
        return PollMapper.to_dto(poll)

    def delete_poll(self, poll_id: str, user_id: str) -> None:
        self._repository.delete(uuid.UUID(poll_id), uuid.UUID(user_id))

    def find_poll_for_user(self, poll_id: str, user_id: str) -> Poll:
        return self._find_poll_or_raise(poll_id, user_id)

    def find_poll(self, poll_id: str) -> Poll:
        poll = self._repository.find_by_id_any_user(uuid.UUID(poll_id))
        if not poll:
            logger.warning(f"Poll retrieval failed. ID {poll_id} not found in data.")
            raise PollNotFoundException(poll_id)
        return poll

    def _find_poll_or_raise(self, poll_id: str, user_id: str) -> Poll:
        poll = self._repository.find_by_id(uuid.UUID(poll_id), uuid.UUID(user_id))
        if not poll:
            logger.warning(f"Poll retrieval failed. ID {poll_id} not found in data.")
            raise PollNotFoundException(poll_id)
        return poll

    def _is_poll_exists(self, poll_id: str) -> bool:
        return self._repository.exists_by_id(uuid.UUID(poll_id))
