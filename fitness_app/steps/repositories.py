from datetime import date

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from fitness_app.steps.models import StepsEntry


class StepsRepository:
    async def save(self, session: AsyncSession, steps_entry: StepsEntry):
        session.add(steps_entry)
        await session.flush()
        await session.commit()
        return steps_entry

    async def get_by_id(self, session: AsyncSession, id: int):
        return await session.get(StepsEntry, id)

    async def get_by_user_id_and_date(
        self, session: AsyncSession, user_id: int, date_field: date
    ):
        q = select(StepsEntry).where(
            StepsEntry.user_id == user_id, StepsEntry.date_field == date_field
        )
        s = await session.execute(q)
        return s.scalar_one_or_none()

    async def get_by_dates(
        self, session: AsyncSession, user_id: int, date_start: date, date_finish: date
    ):
        q = (
            select(StepsEntry)
            .where(
                user_id == user_id,
                StepsEntry.date_field >= date_start,
                StepsEntry.date_field <= date_finish,
            )
            .order_by(StepsEntry.date_field)
        )
        s = await session.execute(q)
        return s.scalars().all()

    async def exists_by_user_id_and_date(
        self, session: AsyncSession, user_id: int, date_field: date
    ):
        q = select(
            exists().where(
                StepsEntry.user_id == user_id, StepsEntry.date_field == date_field
            )
        )
        s = await session.execute(q)
        return s.scalar_one()
