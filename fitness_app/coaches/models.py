from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fitness_app.coaches.schemas import Speciality
from fitness_app.core.db_manager import Base

if TYPE_CHECKING:
    from fitness_app.customers.models import Customer
    from fitness_app.feedbacks.models import Feedback
    from fitness_app.users.models import User
    from fitness_app.workouts.models import Workout


class Coach(Base):
    __tablename__ = "coaches"

    id: Mapped[int] = mapped_column(primary_key=True)
    speciality: Mapped[Speciality] = mapped_column(nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    rating: Mapped[float] = mapped_column(Float, default=5.0, server_default="5.0")

    user: Mapped["User"] = relationship(back_populates="coach_info")
    customers: Mapped[list["Customer"]] = relationship(
        "Customer", back_populates="coaches", secondary="coaches_customers"
    )
    workouts: Mapped[list["Workout"]] = relationship(back_populates="coach")
    feedbacks: Mapped[list["Feedback"]] = relationship(back_populates="coach")
