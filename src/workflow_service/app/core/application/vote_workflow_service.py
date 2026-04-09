import logging
import httpx

from src.workflow_service.app.core.application.protocol import (
    PollServiceProtocol,
    VoteServiceProtocol,
    WorkflowRepositoryProtocol,
)
from src.workflow_service.app.core.domain import WorkflowState
from src.workflow_service.app.core.dto import StartVoteWorkflowDto, WorkflowDto
from src.workflow_service.app.core.mapper import WorkflowMapper
from src.workflow_service.app.core.exception import VoteServiceUnavailableException

logger = logging.getLogger(__name__)


class VoteWorkflowService:
    def __init__(
        self,
        workflow_repo: WorkflowRepositoryProtocol,
        poll_service: PollServiceProtocol,
        vote_service: VoteServiceProtocol,
    ):
        self._workflow_repo = workflow_repo
        self._poll_service = poll_service
        self._vote_service = vote_service

    async def start_vote_workflow(self, dto: StartVoteWorkflowDto) -> WorkflowDto:
        user_id_str = str(dto.user_id)
        poll_id_str = str(dto.poll_id)

        existing_workflow = await self._workflow_repo.find_by_poll_and_user(
            poll_id_str, user_id_str
        )
        if existing_workflow:
            if existing_workflow.state in [WorkflowState.VOTE_SAVED, WorkflowState.PENDING]:
                raise Exception("A vote submission is already in progress")
            if existing_workflow.state == WorkflowState.COMPLETED:
                raise Exception("User has already voted")

        has_voted = await self._vote_service.has_user_voted(poll_id_str, user_id_str)
        if has_voted:
            raise Exception("User has already voted")

        instance = WorkflowMapper.from_start_dto(dto)
        await self._workflow_repo.save(instance)

        is_active = await self._poll_service.is_active(poll_id_str)
        if not is_active:
            WorkflowMapper.advance(instance, error="Poll is not active")
            await self._workflow_repo.save(instance)
            return WorkflowMapper.to_dto(instance)
        

        try:
            answers_dict = [
                {"question_id": str(ans.question_id), "selected_option": ans.selected_option}
                for ans in dto.answers
            ]
            vote_id = await self._vote_service.save_vote(poll_id_str, user_id_str, answers_dict)
            instance.vote_id = vote_id
            WorkflowMapper.advance(instance, state=WorkflowState.VOTE_SAVED)
            await self._workflow_repo.save(instance)
        except (VoteServiceUnavailableException, httpx.TimeoutException) as e:
            logger.error(f"Service unavailable: {e}")
            WorkflowMapper.advance(instance, error=str(e), state=WorkflowState.FAILED)
            await self._workflow_repo.save(instance)
            return WorkflowMapper.to_dto(instance)
        except Exception as e:
            logger.error(f"Failed to save vote for poll {poll_id_str}: {e}")
            WorkflowMapper.advance(instance, error=str(e), state=WorkflowState.FAILED)
            await self._workflow_repo.save(instance)
            return WorkflowMapper.to_dto(instance)

        return WorkflowMapper.to_dto(instance)

    async def get_workflow(self, workflow_id: str) -> WorkflowDto | None:
        instance = await self._workflow_repo.find_by_id(workflow_id)
        if not instance:
            return None
        return WorkflowMapper.to_dto(instance)
