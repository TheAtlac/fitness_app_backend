from datetime import date

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fitness_app.diaries.models import DiaryEntry


class DiaryRepository:
    async def save(self, session: AsyncSession, diary: DiaryEntry):
        session.add(diary)
        await session.flush()
        await session.commit()
        return diary

    async def get_by_user_id_and_date(
        self, session: AsyncSession, user_id: int, date_field: date
    ):
        q = (
            select(DiaryEntry)
            .where(DiaryEntry.user_id == user_id, DiaryEntry.date_field == date_field)
            .options(joinedload(DiaryEntry.voice_note))
        )
        s = await session.execute(q)
        return s.scalar_one_or_none()

    async def get_by_dates(
        self, session: AsyncSession, user_id: int, date_start: date, date_finish: date
    ):
        q = (
            select(DiaryEntry)
            .where(
                user_id == user_id,
                DiaryEntry.date_field >= date_start,
                DiaryEntry.date_field <= date_finish,
            )
            .order_by(DiaryEntry.date_field)
            .options(joinedload(DiaryEntry.voice_note))
        )
        s = await session.execute(q)
        return s.scalars().all()

    async def exists_by_user_id_and_date(
        self, session: AsyncSession, user_id: int, date_field: date
    ):
        q = select(
            exists().where(
                DiaryEntry.user_id == user_id, DiaryEntry.date_field == date_field
            )
        )
        s = await session.execute(q)
        return s.scalar_one()
