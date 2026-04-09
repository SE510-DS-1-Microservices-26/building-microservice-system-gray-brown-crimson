import uuid
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from src.core_service.app.core.events import CoreItemCreatedEvent
from src.core_service.app.core.infrastructure.models import OutboxMessageModel
from src.core_service.app.core.infrastructure.messaging.rabbitmq_publisher import (
    EXCHANGE_NAME,
    ROUTING_KEY,
)

EVENT_TYPE = "CoreItemCreated"


class OutboxRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, event: CoreItemCreatedEvent) -> None:
        row = OutboxMessageModel(
            id=uuid.uuid4(),
            event_type=EVENT_TYPE,
            payload=event.model_dump_json(),
            routing_key=ROUTING_KEY,
            exchange=EXCHANGE_NAME,
            status="pending",
            created_at=datetime.utcnow(),
        )
        self._session.add(row)

    def find_pending(self) -> list[OutboxMessageModel]:
        return (
            self._session.query(OutboxMessageModel)
            .filter(OutboxMessageModel.status == "pending")
            .all()
        )

    def mark_published(self, message_id: UUID) -> None:
        row = self._session.get(OutboxMessageModel, message_id)
        if row:
            row.status = "published"
            row.published_at = datetime.utcnow()
