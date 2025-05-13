from datetime import date

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from fitness_app.water_entries.models import WaterEntry


class WaterEntryRepository:
    async def save(self, session: AsyncSession, water_entry: WaterEntry):
        session.add(water_entry)
        await session.flush()
        await session.commit()
        return water_entry

    async def get_by_id(self, session: AsyncSession, id: int):
        return await session.get(WaterEntry, id)

    async def get_by_user_id_and_date(
        self, session: AsyncSession, user_id: int, date_field: date
    ):
        q = select(WaterEntry).where(
            WaterEntry.user_id == user_id, WaterEntry.date_field == date_field
        )
        s = await session.execute(q)
        return s.scalar_one_or_none()

    async def get_by_dates(
        self, session: AsyncSession, user_id: int, date_start: date, date_finish: date
    ):
        q = (
            select(WaterEntry)
            .where(
                user_id == user_id,
                WaterEntry.date_field >= date_start,
                WaterEntry.date_field <= date_finish,
            )
            .order_by(WaterEntry.date_field)
        )
        s = await session.execute(q)
        return s.scalars().all()

    async def exists_by_user_id_and_date(
        self, session: AsyncSession, user_id: int, date_field: date
    ):
        q = select(
            exists().where(
                WaterEntry.user_id == user_id, WaterEntry.date_field == date_field
            )
        )
        s = await session.execute(q)
        return s.scalar_one()
