from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fitness_app.core.db_manager import Base
from fitness_app.diaries.schemas import Feeling, Reason

if TYPE_CHECKING:
    from fitness_app.file_entities.models import FileEntity
    from fitness_app.users.models import User


class DiaryEntry(Base):
    __tablename__ = "diaries_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    file_entity_id: Mapped[int] = mapped_column(
        ForeignKey("file_entities.id"), nullable=True
    )

    date_field: Mapped[date] = mapped_column(nullable=False)
    feeling: Mapped[Feeling] = mapped_column(nullable=True)
    reason: Mapped[Reason] = mapped_column(nullable=True)
    note: Mapped[str] = mapped_column(nullable=True)

    user: Mapped["User"] = relationship(back_populates="diaries")
    voice_note: Mapped["FileEntity"] = relationship(back_populates="diary")

    __table_args__ = (
        UniqueConstraint("user_id", "date_field", name="uq_diary_user_date"),
    )
