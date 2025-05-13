from datetime import date
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from fitness_app.coaches.models import Coach
from fitness_app.core.db_manager import Base
from fitness_app.core.utils import NonEmptyStr
from fitness_app.customers.models import Customer
from fitness_app.exercises.models import Exercise
from fitness_app.users.schemas import Role, Sex

if TYPE_CHECKING:
    from fitness_app.chats.models import Chat
    from fitness_app.diaries.models import DiaryEntry
    from fitness_app.steps.models import StepsEntry
    from fitness_app.water_entries.models import WaterEntry


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[NonEmptyStr] = mapped_column(unique=True, nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    sex: Mapped[Optional[Sex]] = mapped_column(nullable=True)
    birth_date: Mapped[Optional[date]] = mapped_column(nullable=True)
    password_hash: Mapped[str] = mapped_column(nullable=False)

    exercises: Mapped[list["Exercise"]] = relationship(back_populates="user")

    role: Mapped[Role] = mapped_column(
        server_default="CUSTOMER", default="CUSTOMER", nullable=False
    )

    customer_info: Mapped[Optional["Customer"]] = relationship(
        "Customer", back_populates="user"
    )
    coach_info: Mapped[Optional["Coach"]] = relationship("Coach", back_populates="user")
    chats: Mapped[list["Chat"]] = relationship(
        "Chat", back_populates="users", secondary="chats_users"
    )
    steps_entries: Mapped[list["StepsEntry"]] = relationship(
        "StepsEntry", back_populates="user"
    )
    water_entries: Mapped[list["WaterEntry"]] = relationship(
        "WaterEntry", back_populates="user"
    )
    diaries: Mapped[list["DiaryEntry"]] = relationship(
        "DiaryEntry", back_populates="user"
    )

    __table_args__ = (UniqueConstraint(email),)


class CoachesCustomers(Base):
    __tablename__ = "coaches_customers"

    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id"), primary_key=True
    )
    coach_id: Mapped[int] = mapped_column(ForeignKey("coaches.id"), primary_key=True)

    __table_args__ = (
        UniqueConstraint(
            "customer_id",
            "coach_id",
            name="idx_unique_customer_coach",
        ),
    )
