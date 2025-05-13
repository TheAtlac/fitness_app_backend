from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fitness_app.core.db_manager import Base

if TYPE_CHECKING:
    from fitness_app.file_entities.models import FileEntity
    from fitness_app.users.models import User
    from fitness_app.workouts.models import ExerciseWorkout


class Exercise(Base):
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    originalUri: Mapped[str] = mapped_column(nullable=True)
    name: Mapped[str] = mapped_column(nullable=False)
    muscle: Mapped[str] = mapped_column(nullable=True)
    additionalMuscle: Mapped[str] = mapped_column(nullable=True)
    type: Mapped[str] = mapped_column(nullable=True)
    equipment: Mapped[str] = mapped_column(nullable=True)
    difficulty: Mapped[str] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(nullable=True)

    user: Mapped["User"] = relationship(back_populates="exercises")
    photos: Mapped[list["FileEntity"]] = relationship(
        back_populates="exercise", cascade="all, delete-orphan"
    )
    exercise_workouts: Mapped[list["ExerciseWorkout"]] = relationship(
        back_populates="exercise", cascade="all, delete-orphan"
    )
