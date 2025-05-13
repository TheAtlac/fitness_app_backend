from datetime import date

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fitness_app.core.db_manager import Base
from fitness_app.users.models import User


class StepsEntry(Base):
    __tablename__ = "steps_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    steps: Mapped[int] = mapped_column()
    goal_steps: Mapped[int] = mapped_column()
    date_field: Mapped[date] = mapped_column()

    user: Mapped["User"] = relationship(back_populates="steps_entries")

    __table_args__ = (
        UniqueConstraint("user_id", "date_field", name="uq_steps_user_date"),
    )
