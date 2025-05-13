from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fitness_app.core.db_manager import Base
from fitness_app.workouts.schemas import Stages

if TYPE_CHECKING:
    from fitness_app.chats.models import Chat
    from fitness_app.coaches.models import Coach
    from fitness_app.customers.models import Customer
    from fitness_app.exercises.models import Exercise


class ExerciseWorkout(Base):
    __tablename__ = "exercise_workouts"

    id: Mapped[int] = mapped_column(primary_key=True)
    exercise_id: Mapped[int] = mapped_column(ForeignKey("exercises.id"))
    workout_id: Mapped[int] = mapped_column(ForeignKey("workouts.id"))
    num_order: Mapped[int] = mapped_column(nullable=False)
    num_sets: Mapped[int] = mapped_column(nullable=True)
    num_sets_done: Mapped[int] = mapped_column(nullable=False, default=0)
    num_reps: Mapped[int] = mapped_column(nullable=True)
    stage: Mapped[Stages] = mapped_column(nullable=False)

    exercise: Mapped["Exercise"] = relationship(back_populates="exercise_workouts")
    workout: Mapped["Workout"] = relationship(back_populates="exercise_workouts")


class Workout(Base):
    __tablename__ = "workouts"

    id: Mapped[int] = mapped_column(primary_key=True)
    coach_id: Mapped[int] = mapped_column(ForeignKey("coaches.id"), nullable=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), nullable=True)
    name: Mapped[str] = mapped_column(nullable=False)
    type_connection: Mapped[str] = mapped_column(nullable=True)
    time_start: Mapped[datetime] = mapped_column(nullable=True)

    exercise_workouts: Mapped[Optional[list["ExerciseWorkout"]]] = relationship(
        back_populates="workout", cascade="all, delete-orphan"
    )
    customer: Mapped["Customer"] = relationship(back_populates="workouts")
    coach: Mapped["Coach"] = relationship(back_populates="workouts")
    chat: Mapped["Chat"] = relationship(back_populates="workout")
