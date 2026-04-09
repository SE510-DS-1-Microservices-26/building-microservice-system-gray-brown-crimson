import logging

from uuid import UUID
from src.notification_service.app.core.application.protocol import (
    NotificationRepositoryProtocol,
)
from src.notification_service.app.core.domain import Notification


logger = logging.getLogger(__name__)


class NotificationService:
    def __init__(self, repository: NotificationRepositoryProtocol):
        self._repository = repository

    def save_notification(self, data) -> None:
        notification = Notification(
            event_id=UUID(data.event_id),
            occurred_at=data.occurred_at,
            correlation_id=UUID(data.correlation_id),
            core_item_id=UUID(data.core_item_id),
            owner_user_id=UUID(data.owner_user_id),
            summary=data.summary,
        )
        self._repository.save(notification)
        logger.info(
            "Notification saved: event_id=%s, core_item_id=%s",
            notification.event_id,
            notification.core_item_id,
        )
