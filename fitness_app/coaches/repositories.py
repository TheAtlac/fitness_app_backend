from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fitness_app.coaches.models import Coach
from fitness_app.customers.models import Customer
from fitness_app.feedbacks.models import Feedback
from fitness_app.users.models import CoachesCustomers


class CoachRepository:
    async def save(self, session: AsyncSession, coach: Coach):
        session.add(coach)
        await session.flush()
        await session.commit()
        new_score = await self.get_average_rating(session, coach.id)
        if new_score is None:
            setattr(coach, "rating", 5)
        else:
            setattr(coach, "rating", new_score)
        await session.commit()
        return coach

    async def delete(self, session: AsyncSession, coach: Coach):
        await session.delete(coach)
        await session.commit()
        return coach

    async def get_all(
        self,
        session: AsyncSession,
        page: int,
        size: int,
    ):
        statement = select(Coach).order_by(Coach.id).offset(page * size).limit(size)
        result = await session.execute(statement)
        return result.scalars().all()

    async def get_by_id(
        self,
        session: AsyncSession,
        coach_id: int,
    ):
        statement = (
            select(Coach).where(Coach.id == coach_id).options(joinedload(Coach.user))
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def get_coaches_by_id(
        self,
        session: AsyncSession,
        coach_id: int,
        page: int,
        size: int,
    ):
        statement = (
            select(Customer)
            .join(CoachesCustomers, Customer.id == CoachesCustomers.customer_id)
            .where(CoachesCustomers.coach_id == coach_id)
            .offset(page * size)
            .limit(size)
        )
        result = await session.execute(statement)
        return result.scalars().all()

    async def count_coaches_by_user_id(self, session: AsyncSession, coach_id: int):
        statement = (
            select(func.count(Customer.id))
            .join(Coach.customers)
            .where(Coach.id == coach_id)
        )

        result = await session.execute(statement)
        return result.scalar_one()

    async def count_all(
        self,
        session: AsyncSession,
    ):
        statement = select(func.count()).select_from(Coach)
        result = await session.execute(statement)
        return result.scalar_one()

    async def get_average_rating(self, session: AsyncSession, coach_id: int):
        statement = select(func.avg(Feedback.score)).where(
            Feedback.coach_id == coach_id
        )
        result = await session.execute(statement)
        return result.scalar_one()

    async def add_feedback(
        self, session: AsyncSession, coach_id: int, feedback: Feedback
    ):
        statement = (
            select(Coach)
            .where(Coach.id == coach_id)
            .options(joinedload(Coach.feedbacks))
        )
        result = await session.execute(statement)
        coach = result.unique().scalar_one()
        coach.feedbacks.append(feedback)
        await self.save(session, coach)
