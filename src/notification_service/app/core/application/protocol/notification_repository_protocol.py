from typing import Protocol
from uuid import UUID

from src.notification_service.app.core.domain import Notification


class NotificationRepositoryProtocol(Protocol):
    def save(self, notification: Notification) -> Notification: ...

    def find_by_id(self, event_id: UUID) -> Notification | None: ...
