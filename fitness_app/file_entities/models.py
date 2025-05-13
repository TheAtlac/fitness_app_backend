from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fitness_app.core.db_manager import Base
from fitness_app.diaries.models import DiaryEntry

if TYPE_CHECKING:
    from fitness_app.exercises.models import Exercise


class FileEntity(Base):
    __tablename__ = "file_entities"

    id: Mapped[int] = mapped_column(primary_key=True)
    exercise_id: Mapped[int | None] = mapped_column(
        ForeignKey("exercises.id"), nullable=True
    )
    filename: Mapped[str] = mapped_column(unique=True, nullable=False)

    exercise: Mapped["Exercise"] = relationship(back_populates="photos")
    diary: Mapped["DiaryEntry"] = relationship(back_populates="voice_note")
