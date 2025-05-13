from sqlalchemy.ext.asyncio import AsyncSession

from fitness_app.chats.services import ChatService
from fitness_app.coaches.models import Coach
from fitness_app.coaches.schemas import CoachSchema
from fitness_app.core.exceptions import EntityNotFoundException
from fitness_app.core.schemas import PageSchema
from fitness_app.core.utils import update_model_by_schema
from fitness_app.customers.models import Customer
from fitness_app.customers.repositories import CustomerRepository
from fitness_app.customers.schemas import (
    CustomerCreateSchema,
    CustomerSchema,
    CustomerUpdateSchema,
)
from fitness_app.users.models import User
from fitness_app.users.repositories import UserRepository
from fitness_app.users.schemas import UserCreateSchema
from fitness_app.users.services import UserService


class CustomerService:
    def __init__(
        self,
        customer_repository: CustomerRepository,
        user_repository: UserRepository,
        user_service: UserService,
        chat_service: ChatService,
    ):
        self._customer_repository = customer_repository
        self._user_repository = user_repository
        self._user_service = user_service
        self._chat_service = chat_service

    async def create(self, session: AsyncSession, schema: CustomerCreateSchema):
        userSchema = UserCreateSchema(**schema.model_dump())

        saved_user = await self._user_service.create(session, userSchema)
        customerSchema = CustomerSchema.model_construct(**schema.model_dump())

        customer = Customer(**customerSchema.model_dump())
        setattr(customer, "user_id", saved_user.id)
        setattr(customer, "user", saved_user)
        setattr(customer, "coaches", [])
        setattr(saved_user, "customer_info", customer)
        self._user_repository.save(session, saved_user)
        return await self._customer_repository.save(session, customer)

    async def get_all(
        self,
        session: AsyncSession,
        page: int,
        size: int,
    ):
        total_products_count = await self._customer_repository.count_all(
            session,
        )
        coaches = await self._customer_repository.get_all(session, page, size)
        return PageSchema(total_items_count=total_products_count, items=coaches)

    async def get_current(self, user: User):
        if user is None:
            raise EntityNotFoundException("User with given id was not found")
        if user.customer_info is None:
            raise EntityNotFoundException("User with given id is not a customer")
        return user.customer_info

    async def get_coaches_by_user(
        self,
        session: AsyncSession,
        user: User,
        page: int,
        size: int,
    ):
        if user.customer_info is None:
            raise EntityNotFoundException("User with given id is not a customer")
        own_coaches_count = await self._customer_repository.count_coaches_by_user_id(
            session, user.customer_info.id
        )
        coaches = await self._customer_repository.get_coaches_by_customer_id(
            session, user.customer_info.id, page, size
        )
        return PageSchema(
            total_items_count=own_coaches_count,
            items=list(map(CoachSchema.model_validate, coaches)),
        )

    async def get_by_id(self, session: AsyncSession, customer_id: int):
        customer = await self._customer_repository.get_by_id(session, customer_id)
        if customer is None:
            raise EntityNotFoundException("Customer with given id was not found")

        return customer

    async def assign_coach(self, session: AsyncSession, user: User, coach_id: int):
        customer_id = user.customer_info.id
        users = await self._user_repository.assign_coach_custoemer(
            session=session, customer_id=customer_id, coach_id=coach_id
        )
        await self._chat_service.create(session, users)

        return users[1]

    async def unassign_coach(self, session: AsyncSession, user: User, coach_id: int):
        customer_id = user.customer_info.id
        if await session.get(Coach, customer_id) is None:
            raise EntityNotFoundException("Coach with given id was not found")
        users = await self._user_repository.unassign_coach_custoemer(
            session=session, coach_id=coach_id, customer_id=customer_id
        )
        return users[1]

    async def get_by_user_id(self, session: AsyncSession, user_id: int):
        user = await self._user_service.get_by_id(session, user_id)
        if user is None:
            raise EntityNotFoundException("User with given id was not found")
        if user.customer_info is None:
            raise EntityNotFoundException("User with given id is not a customer")

        return user.customer_info

    async def update_by_user(
        self, session: AsyncSession, schema: CustomerUpdateSchema, user: User
    ):
        customer = user.customer_info
        if customer is None:
            raise EntityNotFoundException("User with given id is not a customer")

        update_model_by_schema(customer, schema)

        return await self._customer_repository.save(session, customer)

    async def delete_by_id(self, session: AsyncSession, customer_id: int):
        customer = await session.get(Customer, customer_id)
        if customer is None:
            raise EntityNotFoundException("Coach with given id was not found")
        self._user_service.delete_by_id(session, customer.user_id)
        return await self._customer_repository.delete(session, customer)
