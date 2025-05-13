from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fitness_app.core.db_manager import Base

if TYPE_CHECKING:
    from fitness_app.coaches.models import Coach
    from fitness_app.customers.models import Customer


class Feedback(Base):
    __tablename__ = "feedbacks"

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"), primary_key=True
    )
    coach_id: Mapped[int] = mapped_column(ForeignKey("coaches.id"), primary_key=True)
    score: Mapped[int]
    customer: Mapped["Customer"] = relationship("Customer", back_populates="feedbacks")
    coach: Mapped["Coach"] = relationship("Coach", back_populates="feedbacks")

    __table_args__ = (
        UniqueConstraint(
            "customer_id",
            "coach_id",
            name="idx_unique_feedback",
        ),
    )
