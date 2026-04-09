from datetime import datetime
from uuid import UUID
from sqlalchemy import Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from .database import Base


class CoreItemCreatedEventModel(Base):
    __tablename__ = "core_item_created_events"

    event_id: Mapped[UUID] = mapped_column(primary_key=True, unique=True)
    occurred_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    correlation_id: Mapped[UUID] = mapped_column(nullable=False)
    core_item_id: Mapped[UUID] = mapped_column(nullable=False)
    owner_user_id: Mapped[UUID] = mapped_column(nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
