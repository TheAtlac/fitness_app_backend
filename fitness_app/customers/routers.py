from typing import Annotated

from fastapi import APIRouter, Depends, Path

from fitness_app.auth.dependencies import AuthenticateUser, HasPermission
from fitness_app.auth.permissions import IsCustomer
from fitness_app.core.dependencies import CustomerServiceDep, DbSession
from fitness_app.core.schemas import PageSchema
from fitness_app.core.utils import IdField, PageField, SizeField
from fitness_app.customers.schemas import (
    CustomerCreateSchema,
    CustomerSchema,
    CustomerUpdateSchema,
)
from fitness_app.users.schemas import UserSchema

customers_router = APIRouter(prefix="/customers", tags=["Клиенты"])


@customers_router.get(
    "/",
    summary="Получить список всех клиентов",
    response_model=PageSchema,
)
async def get_all(
    session: DbSession,
    service: CustomerServiceDep,
    page: PageField = 0,
    size: SizeField = 10,
):
    customers = await service.get_all(session, page, size)
    return PageSchema(
        total_items_count=customers.total_items_count,
        items=list(map(CustomerSchema.model_validate, customers.items)),
    )


@customers_router.get(
    "/id/{customer_id}",
    summary="Получить клиента по customer_id",
    response_model=CustomerSchema,
)
async def get(
    session: DbSession,
    service: CustomerServiceDep,
    customer_id: IdField,
):
    customer = await service.get_by_id(session, customer_id)
    return CustomerSchema.model_validate(customer)


@customers_router.get(
    "/user_id/{user_id}",
    summary="Получить клиента по user_id",
    response_model=CustomerSchema,
    # dependencies=[Depends(HasPermission(Authenticated()))],
)
async def get_by_user_id(
    session: DbSession,
    service: CustomerServiceDep,
    user_id: IdField,
):
    customer = await service.get_by_user_id(session, user_id)
    return CustomerSchema.model_validate(customer)


@customers_router.post(
    "/registration",
    summary="Создать клиента",
    response_model=CustomerSchema,
    # dependencies=[Depends(HasPermission(Anonymous()))],
)
async def create(
    session: DbSession,
    service: CustomerServiceDep,
    schema: CustomerCreateSchema,
):
    customer = await service.create(session, schema)
    return CustomerSchema.model_validate(customer, from_attributes=True)


@customers_router.get(
    "/current",
    summary="Получить текущего авторизованного клиента",
    response_model=CustomerSchema,
    dependencies=[Depends(HasPermission(IsCustomer()))],
)
async def get_current_customer(
    service: CustomerServiceDep,
    user: AuthenticateUser,
):
    customer = await service.get_current(user)
    return CustomerSchema.model_validate(customer)


@customers_router.put(
    "/current",
    response_model=CustomerSchema,
    summary="Обновить текущего авторизованного клиента",
    dependencies=[Depends(HasPermission(IsCustomer()))],
)
async def put_current_customer(
    user: AuthenticateUser,
    service: CustomerServiceDep,
    session: DbSession,
    schema: CustomerUpdateSchema,
):
    customer = await service.update_by_user(session, schema, user)
    return CustomerSchema.model_validate(customer)


@customers_router.get(
    "/my_coaches",
    response_model=PageSchema,
    summary="Получение своих тренеров",
    dependencies=[Depends(HasPermission(IsCustomer()))],
)
async def get_coaches(
    user: AuthenticateUser,
    service: CustomerServiceDep,
    session: DbSession,
    page: PageField = 0,
    size: SizeField = 10,
):
    coaches = await service.get_coaches_by_user(session, user, page, size)
    return coaches


@customers_router.post(
    "/assign_me_coach/{coach_id}",
    response_model=UserSchema,
    summary="Назначение тренера текущему клиенту",
    dependencies=[Depends(HasPermission(IsCustomer()))],
)
async def assign_coach(
    user: AuthenticateUser,
    service: CustomerServiceDep,
    session: DbSession,
    coach_id: Annotated[int, Path],
):
    coach = await service.assign_coach(session, user, coach_id)
    return UserSchema.model_validate(coach)


@customers_router.post(
    "/unassign_me_coach/{coach_id}",
    response_model=UserSchema,
    summary="Отвязка текущего клиента от тренера",
    dependencies=[Depends(HasPermission(IsCustomer()))],
)
async def unassign_coach(
    user: AuthenticateUser,
    service: CustomerServiceDep,
    session: DbSession,
    coach_id: Annotated[int, Path],
):
    coach = await service.unassign_coach(session, user, coach_id)
    return UserSchema.model_validate(coach)
