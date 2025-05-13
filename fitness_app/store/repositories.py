from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from fitness_app.store.models import Product
from fitness_app.store.schemas import ProductCategory


class StoreRepository:

    async def get_by_id(self, session: AsyncSession, id: int) -> Product | None:
        statement = select(Product).where(Product.id == id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        session: AsyncSession,
        page: int,
        size: int,
        category: ProductCategory,
        name_part: str,
    ):
        statement = select(Product).order_by(Product.id)
        if category:
            statement = statement.filter(Product.category == category)
        if name_part:
            statement = statement.where(Product.name.icontains(name_part))
        statement = statement.offset(page * size).limit(size)
        result = await session.execute(statement)
        return result.scalars().all()

    async def count_all(
        self,
        session: AsyncSession,
        category,
        name_part,
    ):
        statement = select(func.count()).select_from(Product)
        if category:
            statement = statement.filter(Product.category == category)
        if name_part:
            statement = statement.filter(Product.name.icontains(name_part))
        result = await session.execute(statement)
        return result.scalar_one()

    async def save(self, session: AsyncSession, product: Product) -> Product:
        session.add(product)
        await session.flush()
        await session.commit()
        return product

    async def delete(self, session: AsyncSession, product: Product):
        await session.delete(product)
        await session.commit()
