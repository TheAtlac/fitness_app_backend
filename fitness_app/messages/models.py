from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ARRAY, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fitness_app.core.db_manager import Base

if TYPE_CHECKING:
    from fitness_app.chats.models import Chat


class Message(Base):
    __tablename__ = "messages"

    chat: Mapped["Chat"] = relationship("Chat", back_populates="messages")
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content: Mapped[Optional[str]] = mapped_column(nullable=True)
    timestamp: Mapped[datetime] = mapped_column(
        default=datetime.now, server_default=func.now()
    )
    files_urls: Mapped[list[str]] = mapped_column(ARRAY(Text))
    voice_url: Mapped[Optional[str]] = mapped_column(nullable=True)

    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"))
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
