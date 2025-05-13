from sqlalchemy.ext.asyncio import AsyncSession

from fitness_app.auth.services import PasswordService
from fitness_app.core.exceptions import (
    EntityAlreadyExistsException,
    EntityNotFoundException,
)
from fitness_app.core.schemas import PageSchema
from fitness_app.core.utils import update_model_by_schema
from fitness_app.users.models import User
from fitness_app.users.repositories import UserRepository
from fitness_app.users.schemas import UserCreateSchema, UserUpdateSchema


class UserService:
    def __init__(
        self,
        password_service: PasswordService,
        user_repository: UserRepository,
    ):
        self._password_service = password_service
        self._user_repository = user_repository

    async def get_all(
        self,
        session: AsyncSession,
        page: int,
        size: int,
    ):
        total_products_count = await self._user_repository.count_all(
            session,
        )
        users = await self._user_repository.get_all(
            session,
            page,
            size,
        )
        return PageSchema(total_items_count=total_products_count, items=users)

    async def create(self, session: AsyncSession, schema: UserCreateSchema):
        if await self._user_repository.exists_by_email(session, schema.email):
            raise EntityAlreadyExistsException("User with given login already exists")

        user = User(**schema.model_dump(exclude=["password"], exclude_unset=True))
        user.password_hash = self._password_service.get_password_hash(schema.password)
        user.coach_info = None
        user.customer_info = None
        await self._user_repository.save(session, user)

        return user

    async def get_by_id(self, session: AsyncSession, id: int):
        user = await self._user_repository.get_by_id(session, id)
        if user is None:
            raise EntityNotFoundException("User with given id was not found")

        return user

    async def update_by_id(
        self, session: AsyncSession, id: int, schema: UserUpdateSchema
    ):
        user = await self._user_repository.get_by_id(session, id)
        if user is None:
            raise EntityNotFoundException("User with given id was not found")

        if schema.email != user.email and await self._user_repository.exists_by_email(
            session, schema.email
        ):
            raise EntityAlreadyExistsException("User with given login already exists")

        update_model_by_schema(user, schema)

        return await self._user_repository.save(session, user)

    async def update_password_by_id(
        self, session: AsyncSession, id: int, password: str
    ):
        user = await self._user_repository.get_by_id(session, id)
        if user is None:
            raise EntityNotFoundException("User with given id was not found")

        user.password_hash = self._password_service.get_password_hash(password)

        return await self._user_repository.save(session, user)

    async def delete_by_id(self, session: AsyncSession, id: int):
        user = await self._user_repository.get_by_id(session, id)
        if user is None:
            raise EntityNotFoundException("User with given id was not found")

        return await self._user_repository.delete(session, user)
