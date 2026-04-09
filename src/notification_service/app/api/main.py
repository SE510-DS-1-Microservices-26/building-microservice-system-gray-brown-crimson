import asyncio
import logging
from faststream import FastStream
from faststream.rabbit import RabbitBroker, RabbitExchange, RabbitQueue
from faststream.rabbit import ExchangeType

from src.notification_service.app.core.infrastructure import SessionLocal
from src.notification_service.app.core.infrastructure.repository import NotificationRepository
from src.notification_service.app.core.application.notification_service import NotificationService
from src.notification_service.app.core.dto import CoreItemCreatedEventSchema
from src.notification_service.app.shared.settings import settings


logger = logging.getLogger(__name__)

broker = RabbitBroker(settings.rabbitmq_url)
app = FastStream(broker)

core_exchange = RabbitExchange("core", type=ExchangeType.DIRECT, durable=True)
notifications_queue = RabbitQueue("notifications.core-item.created", routing_key="core-item.created")


def _save_notification_sync(msg: CoreItemCreatedEventSchema) -> None:
    session = SessionLocal()
    try:
        repository = NotificationRepository(session)
        service = NotificationService(repository)
        service.save_notification(msg)
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@broker.subscriber(notifications_queue, core_exchange)
async def handle(msg: CoreItemCreatedEventSchema):
    try:
        await asyncio.to_thread(_save_notification_sync, msg)
        logger.info(
            "Notification processed: event_id=%s, core_item_id=%s",
            msg.event_id,
            msg.core_item_id,
        )
    except Exception as exc:
        logger.error(
            "Error processing notification: event_id=%s, error=%s",
            msg.event_id,
            exc,
            exc_info=True,
        )
        raise
