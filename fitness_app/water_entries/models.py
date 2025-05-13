from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fitness_app.core.db_manager import Base

if TYPE_CHECKING:
    from fitness_app.users.models import User


class WaterEntry(Base):
    __tablename__ = "water_entries"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    water_volume: Mapped[int] = mapped_column()
    goal_water_volume: Mapped[int] = mapped_column()
    date_field: Mapped[date] = mapped_column()

    user: Mapped["User"] = relationship(back_populates="water_entries")

    __table_args__ = (
        UniqueConstraint("user_id", "date_field", name="uq_water_entities_user_date"),
    )
