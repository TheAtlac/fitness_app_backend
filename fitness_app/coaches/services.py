from sqlalchemy.ext.asyncio import AsyncSession

from fitness_app.chats.services import ChatService
from fitness_app.coaches.models import Coach
from fitness_app.coaches.repositories import CoachRepository
from fitness_app.coaches.schemas import (
    CoachCreateSchema,
    CoachSchema,
    CoachUpdateSchema,
)
from fitness_app.core.exceptions import EntityNotFoundException
from fitness_app.core.schemas import PageSchema
from fitness_app.core.utils import update_model_by_schema
from fitness_app.customers.models import Customer
from fitness_app.customers.schemas import CustomerSchema
from fitness_app.users.models import User
from fitness_app.users.repositories import UserRepository
from fitness_app.users.schemas import UserCreateSchema
from fitness_app.users.services import UserService


class CoachService:
    def __init__(
        self,
        coach_repository: CoachRepository,
        user_repository: UserRepository,
        user_service: UserService,
        chat_service: ChatService,
    ):
        self._coach_repository = coach_repository
        self._user_repository = user_repository
        self._user_service = user_service
        self._chat_service = chat_service

    async def create(self, session: AsyncSession, schema: CoachCreateSchema):
        userSchema = UserCreateSchema(**schema.model_dump())

        saved_user = await self._user_service.create(session, userSchema)
        coachSchema = CoachSchema.model_construct(**schema.model_dump())
        coach = Coach(**coachSchema.model_dump())
        setattr(coach, "user_id", saved_user.id)
        setattr(coach, "user", saved_user)
        setattr(coach, "customers", [])
        setattr(coach, "feedbacks", [])
        setattr(saved_user, "role", "COACH")
        setattr(saved_user, "coach_info", coach)
        self._user_repository.save(session, saved_user)
        return await self._coach_repository.save(session, coach)

    async def get_all(
        self,
        session: AsyncSession,
        page: int,
        size: int,
    ):
        total_products_count = await self._coach_repository.count_all(
            session,
        )
        coaches = await self._coach_repository.get_all(session, page, size)
        return PageSchema(total_items_count=total_products_count, items=coaches)

    async def get_current(self, user: User):
        if user is None:
            raise EntityNotFoundException("User with given id was not found")
        if user.coach_info is None:
            raise EntityNotFoundException("User with given id is not a coach")
        return user.coach_info

    async def get_by_id(self, session: AsyncSession, coach_id: int):
        coach = await self._coach_repository.get_by_id(session, coach_id)
        if coach is None:
            raise EntityNotFoundException("Coach with given id was not found")

        return coach

    async def get_by_user_id(self, session: AsyncSession, user_id: int):
        user = await self._user_service.get_by_id(session, user_id)
        if user is None:
            raise EntityNotFoundException("User with given id was not found")
        if user.coach_info is None:
            raise EntityNotFoundException("User with given id is not a coach")

        return user.coach_info

    async def update_by_user(
        self, session: AsyncSession, schema: CoachUpdateSchema, user: User
    ):
        coach = user.coach_info
        if coach is None:
            raise EntityNotFoundException("Coach with given id was not found")

        update_model_by_schema(coach, schema)

        return await self._coach_repository.save(session, coach)

    async def get_customers_by_user(
        self,
        session: AsyncSession,
        user: User,
        page: int,
        size: int,
    ):
        if user.coach_info is None:
            raise EntityNotFoundException("User with given id is not a coach")
        own_coaches_count = await self._coach_repository.count_coaches_by_user_id(
            session, user.coach_info.id
        )
        coaches = await self._coach_repository.get_coaches_by_id(
            session, user.coach_info.id, page, size
        )
        return PageSchema(
            total_items_count=own_coaches_count,
            items=list(map(CustomerSchema.model_validate, coaches)),
        )

    async def assign_customer(
        self, session: AsyncSession, user: User, customer_id: int
    ):
        coach_id = user.coach_info.id
        if await session.get(Customer, customer_id) is None:
            raise EntityNotFoundException("Customer with given id was not found")
        users = await self._user_repository.assign_coach_custoemer(
            session=session, coach_id=coach_id, customer_id=customer_id
        )
        await self._chat_service.create(session, users)
        return users[0]

    async def unassign_customer(
        self, session: AsyncSession, user: User, customer_id: int
    ):
        coach_id = user.coach_info.id
        if await session.get(Customer, customer_id) is None:
            raise EntityNotFoundException("Customer with given id was not found")
        users = await self._user_repository.unassign_coach_custoemer(
            session=session, coach_id=coach_id, customer_id=customer_id
        )
        return users[0]

    async def delete_by_id(self, session: AsyncSession, coach_id: int):
        coach = await session.get(Coach, coach_id)
        if coach is None:
            raise EntityNotFoundException("Coach with given id was not found")
        self._user_service.delete_by_id(session, coach.user_id)

        return await self._coach_repository.delete(session, coach)
