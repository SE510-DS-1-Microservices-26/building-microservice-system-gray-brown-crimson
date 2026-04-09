from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy.dialects.postgresql import insert as pg_insert
from src.notification_service.app.core.domain import Notification

from ..models import CoreItemCreatedEventModel


class NotificationRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, notification: Notification) -> Notification:
        stmt = (
            pg_insert(CoreItemCreatedEventModel)
            .values(
                event_id=notification.event_id,
                occurred_at=notification.occurred_at,
                correlation_id=notification.correlation_id,
                core_item_id=notification.core_item_id,
                owner_user_id=notification.owner_user_id,
                summary=notification.summary,
            )
            .on_conflict_do_nothing(index_elements=['event_id'])
        )
        self._session.execute(stmt)
        self._session.commit()
        return notification

    def find_by_id(self, event_id: UUID) -> Notification | None:
        row = self._session.get(CoreItemCreatedEventModel, event_id)
        return self._to_domain(row) if row else None

    @staticmethod
    def _to_domain(row: CoreItemCreatedEventModel) -> Notification:
        return Notification(
            event_id=row.event_id,
            occurred_at=row.occurred_at,
            correlation_id=row.correlation_id,
            core_item_id=row.core_item_id,
            owner_user_id=row.owner_user_id,
            summary=row.summary,
        )