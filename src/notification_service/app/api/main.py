from faststream import FastStream
from faststream.rabbit import RabbitBroker

from src.notification_service.app.core.infrastructure import SessionLocal
from src.notification_service.app.core.infrastructure.repository import NotificationRepository
from src.notification_service.app.core.application.notification_service import NotificationService
from src.notification_service.app.core.dto import CoreItemCreatedEventSchema
from src.notification_service.app.shared.settings import settings


broker = RabbitBroker(settings.rabbitmq_url)
app = FastStream(broker)


@broker.subscriber("core-item.created")
async def handle(msg: CoreItemCreatedEventSchema):
    session = SessionLocal()
    try:
        repository = NotificationRepository(session)
        service = NotificationService(repository)
        service.save_notification(msg)
    except:
        session.rollback()
        raise
    finally:
        session.close()
