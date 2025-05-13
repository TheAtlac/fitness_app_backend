from sqlalchemy.ext.asyncio import AsyncSession

from fitness_app.core.exceptions import EntityNotFoundException
from fitness_app.core.schemas import PageSchema
from fitness_app.core.utils import update_model_by_schema
from fitness_app.store.models import Product
from fitness_app.store.repositories import StoreRepository
from fitness_app.store.schemas import (
    ProductCategory,
    ProductCreateSchema,
    ProductSchema,
)


class StoreService:
    def __init__(self, store_repository: StoreRepository):
        self._store_repository = store_repository

    async def create(
        self,
        session: AsyncSession,
        schema: ProductCreateSchema,
    ):
        product = Product(**schema.model_dump())
        return await self._store_repository.save(session, product)

    async def get_by_id(self, session: AsyncSession, id: int) -> Product:
        product = await self._store_repository.get_by_id(session, id)
        if product is None:
            raise EntityNotFoundException("Product with given `id` was not found")
        return product

    async def get_all(
        self,
        session: AsyncSession,
        page: int,
        size: int,
        category: ProductCategory,
        name_part: str,
    ) -> PageSchema:
        total_products_count = await self._store_repository.count_all(
            session,
            category,
            name_part,
        )
        products = await self._store_repository.get_all(
            session, page, size, category, name_part
        )
        return PageSchema(total_items_count=total_products_count, items=products)

    async def update_by_id(
        self, session: AsyncSession, id: int, schema: ProductCreateSchema
    ) -> Product:
        product = await self._store_repository.get_by_id(session, id)
        if product is None:
            raise EntityNotFoundException("Product with given id was not found")

        update_model_by_schema(product, schema)
        return await self._store_repository.save(session, product)

    async def delete_by_id(self, session: AsyncSession, id: int):
        product = await self._store_repository.get_by_id(session, id)
        if product is None:
            raise EntityNotFoundException("Product with given id was not found")

        await self._store_repository.delete(session, product)
        return ProductSchema.model_validate(product)
