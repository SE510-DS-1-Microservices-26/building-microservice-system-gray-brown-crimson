import logging

import aio_pika

from src.core_service.app.core.events import CoreItemCreatedEvent

logger = logging.getLogger(__name__)

EXCHANGE_NAME = "core"
ROUTING_KEY = "core-item.created"


class RabbitMQPublisher:
    def __init__(self, url: str) -> None:
        self._url = url
        self._connection: aio_pika.abc.AbstractConnection | None = None
        self._exchange: aio_pika.abc.AbstractExchange | None = None

    async def connect(self) -> None:
        self._connection = await aio_pika.connect_robust(self._url)
        channel = await self._connection.channel()
        self._exchange = await channel.declare_exchange(
            EXCHANGE_NAME,
            aio_pika.ExchangeType.DIRECT,
            durable=True,
        )
        logger.info("RabbitMQ publisher connected (exchange: %s)", EXCHANGE_NAME)

    async def publish(self, event: CoreItemCreatedEvent) -> None:
        if self._exchange is None:
            logger.error("RabbitMQ publisher is not connected; cannot publish")
            raise RuntimeError("RabbitMQ publisher is not connected")
        body = event.model_dump_json().encode()
        message = aio_pika.Message(
            body=body,
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )
        await self._exchange.publish(message, routing_key=ROUTING_KEY)
        logger.info("Published %s (core_item_id=%s)", ROUTING_KEY, event.core_item_id)

    async def close(self) -> None:
        if self._connection and not self._connection.is_closed:
            await self._connection.close()
            logger.info("RabbitMQ publisher connection closed")
