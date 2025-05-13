from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fitness_app.core.db_manager import Base
from fitness_app.customers.schemas import ExercisePreference, FitnessLevel, UserGoal

if TYPE_CHECKING:
    from fitness_app.coaches.models import Coach
    from fitness_app.feedbacks.models import Feedback
    from fitness_app.users.models import User
    from fitness_app.workouts.models import Workout


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    goal: Mapped[Optional[UserGoal]]
    fitness_level: Mapped[Optional[FitnessLevel]]
    preference: Mapped[Optional[ExercisePreference]]

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    user: Mapped["User"] = relationship(back_populates="customer_info")

    coaches: Mapped[list["Coach"]] = relationship(
        "Coach", back_populates="customers", secondary="coaches_customers"
    )
    workouts: Mapped[list["Workout"]] = relationship(back_populates="customer")
    feedbacks: Mapped[list["Feedback"]] = relationship(back_populates="customer")
