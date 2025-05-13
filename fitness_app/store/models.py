from sqlalchemy import ARRAY, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from fitness_app.core.db_manager import Base
from fitness_app.store.schemas import ProductCategory


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)
    price: Mapped[int] = mapped_column(nullable=False)
    category: Mapped[ProductCategory] = mapped_column(nullable=False)
    link: Mapped[str] = mapped_column(nullable=False)
    images: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False)

    __table_args__ = (UniqueConstraint(id),)
