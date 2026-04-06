import asyncio
import logging

from src.core_service.app.core.events import CoreItemCreatedEvent
from src.core_service.app.core.infrastructure.database import SessionLocal
from src.core_service.app.core.infrastructure.rabbitmq_publisher import (
    RabbitMQPublisher,
)
from src.core_service.app.core.infrastructure.repository import OutboxRepository

logger = logging.getLogger(__name__)


async def run_outbox_relay(publisher: RabbitMQPublisher, interval: float = 2.0) -> None:
    logger.info("Outbox relay started (interval=%.1fs)", interval)
    while True:
        await asyncio.sleep(interval)
        try:
            with SessionLocal() as session:
                repo = OutboxRepository(session)
                rows = repo.find_pending()
                if not rows:
                    continue
                for row in rows:
                    try:
                        event = CoreItemCreatedEvent.model_validate_json(row.payload)
                        await publisher.publish(event)
                        repo.mark_published(row.id)
                        logger.info(
                            "Outbox: published message id=%s event_type=%s",
                            row.id,
                            row.event_type,
                        )
                    except Exception:
                        logger.exception(
                            "Outbox: failed to publish message id=%s; will retry",
                            row.id,
                        )
                session.commit()
        except Exception:
            logger.exception("Outbox relay encountered an error; continuing")
