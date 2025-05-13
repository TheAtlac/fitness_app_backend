from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fitness_app.coaches.models import Coach
from fitness_app.customers.models import Customer
from fitness_app.users.models import CoachesCustomers


class CustomerRepository:

    async def save(self, session: AsyncSession, customer: Customer):
        session.add(customer)
        await session.flush()
        await session.commit()
        return customer

    async def delete(self, session: AsyncSession, customer: Customer):
        await session.delete(customer)
        await session.commit()
        return customer

    async def get_all(
        self,
        session: AsyncSession,
        page: int,
        size: int,
    ):
        statement = (
            select(Customer).order_by(Customer.id).offset(page * size).limit(size)
        )
        result = await session.execute(statement)
        return result.scalars().all()

    async def get_by_id(
        self,
        session: AsyncSession,
        customer_id: int,
    ):
        statement = (
            select(Customer)
            .where(Customer.id == customer_id)
            .options(joinedload(Customer.user))
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def count_all(
        self,
        session: AsyncSession,
    ):
        statement = select(func.count()).select_from(Customer)
        result = await session.execute(statement)
        return result.scalar_one()

    async def get_coaches_by_customer_id(
        self,
        session: AsyncSession,
        customer_id: int,
        page: int,
        size: int,
    ):
        statement = (
            select(Coach)
            .join(CoachesCustomers, Coach.id == CoachesCustomers.coach_id)
            .where(CoachesCustomers.customer_id == customer_id)
            .offset(page * size)
            .limit(size)
        )
        result = await session.execute(statement)
        return result.scalars().all()

    async def count_coaches_by_user_id(self, session: AsyncSession, customer_id: int):
        statement = (
            select(func.count(Coach.id))
            .join(Customer.coaches)
            .where(Customer.id == customer_id)
        )

        result = await session.execute(statement)
        return result.scalar_one()
