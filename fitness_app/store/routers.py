from fastapi import APIRouter, Depends, status

from fitness_app.auth.dependencies import HasPermission
from fitness_app.auth.permissions import Authenticated
from fitness_app.core.dependencies import DbSession, StoreServiceDep
from fitness_app.core.schemas import PageSchema
from fitness_app.core.utils import IdField, PageField, SizeField
from fitness_app.store.schemas import (
    ProductCategory,
    ProductCreateSchema,
    ProductSchema,
)

store_router = APIRouter(prefix="/store", tags=["Магазин"])


@store_router.post(
    "",
    summary="Добавление нового товара",
    response_model=ProductSchema,
    responses={
        status.HTTP_409_CONFLICT: {
            "description": "Другой товар c указанным `name` уже существует"
        }
    },
    dependencies=[Depends(HasPermission(Authenticated()))],
)
async def create_product(
    session: DbSession,
    service: StoreServiceDep,
    schema: ProductCreateSchema,
):
    product = await service.create(session, schema)
    return ProductSchema.model_validate(product)


@store_router.get(
    "/{product_id}",
    summary="Получить товар по `id`",
    response_model=ProductSchema,
)
async def get_product_by_id(
    session: DbSession,
    service: StoreServiceDep,
    product_id: IdField,
):
    product = await service.get_by_id(session, product_id)
    return ProductSchema.model_validate(product)


@store_router.get(
    "",
    summary="Получить список товаров",
)
async def get_all_products(
    session: DbSession,
    service: StoreServiceDep,
    page: PageField = 0,
    size: SizeField = 10,
    category: ProductCategory | None = None,
    name: str = None,
):
    products = await service.get_all(session, page, size, category, name)
    return PageSchema(
        total_items_count=products.total_items_count,
        items=list(map(ProductSchema.model_validate, products.items)),
    )


@store_router.put(
    "/{product_id}",
    summary="Обновить товар полностью",
    response_model=ProductSchema,
    dependencies=[Depends(HasPermission(Authenticated()))],
)
async def update_product_by_id(
    session: DbSession,
    service: StoreServiceDep,
    product_id: IdField,
    schema: ProductCreateSchema,
):
    product = await service.update_by_id(session, product_id, schema)
    return ProductSchema.model_validate(product)


@store_router.delete(
    "/{product_id}",
    summary="Удалить товар по id",
    response_model=ProductSchema,
    dependencies=[Depends(HasPermission(Authenticated()))],
)
async def delete(
    session: DbSession,
    service: StoreServiceDep,
    product_id: IdField,
):
    product = await service.delete_by_id(session, product_id)
    return ProductSchema.model_validate(product)
