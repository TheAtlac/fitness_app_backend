from sqlalchemy import and_, exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from fitness_app.coaches.models import Coach
from fitness_app.core.exceptions import (
    EntityAlreadyExistsException,
    EntityNotFoundException,
)
from fitness_app.customers.models import Customer
from fitness_app.users.models import CoachesCustomers, User


class UserRepository:
    async def get_by_id(self, session: AsyncSession, id: int):
        # return await session.get(User, id)
        statement = (
            select(User)
            .where(User.id == id)
            .options(joinedload(User.coach_info), joinedload(User.customer_info))
        )

        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_email(self, session: AsyncSession, email: str):
        statement = select(User).where(User.email == email)
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def exists_by_email(self, session: AsyncSession, email: str):
        statement = select(exists().where(User.email == email))
        result = await session.execute(statement)
        return result.scalar_one()

    async def get_all(self, session: AsyncSession, page: int, size: int):
        statement = select(User).order_by(User.id).offset(page * size).limit(size)
        result = await session.execute(statement)
        return result.scalars().all()

    async def count_all(self, session: AsyncSession):
        statement = select(func.count()).select_from(User)
        result = await session.execute(statement)
        return result.scalar_one()

    async def is_exists_assignment(
        self, session: AsyncSession, customer_id: int, coach_id: int
    ):
        statement = select(
            exists().where(
                (
                    and_(
                        CoachesCustomers.customer_id == customer_id,
                        CoachesCustomers.coach_id == coach_id,
                    )
                )
            )
        )
        result = await session.execute(statement)
        return result.scalar_one()

    async def assign_coach_custoemer(
        self, session: AsyncSession, customer_id: int, coach_id: int
    ) -> Coach:
        if await self.is_exists_assignment(session, customer_id, coach_id):
            raise EntityAlreadyExistsException(
                "coach already assigned to to this customer"
            )
        customer_statement = (
            select(Customer)
            .where(Customer.id == customer_id)
            .options(selectinload(Customer.coaches), joinedload(Customer.user))
        )

        customer_result = await session.execute(customer_statement)
        customer = customer_result.scalar_one_or_none()
        if customer is None:
            raise EntityNotFoundException("customer with given id was not found")
        coach_statement = (
            select(Coach)
            .where(Coach.id == coach_id)
            .options(selectinload(Coach.customers), joinedload(Coach.user))
        )
        coach_result = await session.execute(coach_statement)

        coach = coach_result.scalar_one_or_none()
        if coach is None:
            raise EntityNotFoundException("coach with given id was not found")
        users = [customer.user, coach.user]

        if coach not in customer.coaches:
            customer.coaches.append(coach)

        if customer not in coach.customers:
            coach.customers.append(customer)

        await session.commit()
        return users

    async def unassign_coach_custoemer(
        self, session: AsyncSession, customer_id: int, coach_id: int
    ) -> Coach:
        if not await self.is_exists_assignment(session, customer_id, coach_id):
            raise EntityAlreadyExistsException(
                "coach is not assigned to to this customer yet"
            )
        customer_statement = (
            select(Customer)
            .where(Customer.id == customer_id)
            .options(selectinload(Customer.coaches), joinedload(Customer.user))
        )
        customer_result = await session.execute(customer_statement)
        customer = customer_result.scalar_one()
        coach_statement = (
            select(Coach)
            .where(Coach.id == coach_id)
            .options(selectinload(Coach.customers), joinedload(Coach.user))
        )

        coach_result = await session.execute(coach_statement)

        coach = coach_result.scalar_one()
        users = [customer.user, coach.user]

        if coach in customer.coaches:
            customer.coaches.remove(coach)

        if customer in coach.customers:
            coach.customers.remove(customer)
        await session.flush()
        await session.commit()
        return users

    async def save(self, session: AsyncSession, user: User):
        session.add(user)
        await session.flush()
        await session.commit()
        return user

    async def delete(self, session: AsyncSession, user: User):
        await session.delete(user)
        await session.commit()
        return user
