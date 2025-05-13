from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from fitness_app.core.utils import update_model_by_schema
from fitness_app.water_entries.models import WaterEntry
from fitness_app.water_entries.repositories import WaterEntryRepository
from fitness_app.water_entries.schemas import WaterEntryCreateSchema


class WaterEntryService:
    def __init__(
        self, water_entry_repository: WaterEntryRepository, goal_water_volume: int
    ):
        self._water_entry_repository = water_entry_repository
        self._goal_water_volume = goal_water_volume

    async def get_by_dates(
        self, session: AsyncSession, user_id: int, date_start: date, date_finish: date
    ) -> list[WaterEntry]:
        water_entries = await self._water_entry_repository.get_by_dates(
            session, user_id, date_start, date_finish
        )

        return water_entries

    async def create_or_update(
        self, session: AsyncSession, user_id: int, schema: WaterEntryCreateSchema
    ):
        curr_date = date.today()
        if await self._water_entry_repository.exists_by_user_id_and_date(
            session, user_id, curr_date
        ):
            waters_entry = await self._water_entry_repository.get_by_user_id_and_date(
                session, user_id, curr_date
            )
            update_model_by_schema(waters_entry, schema)
        else:
            waters_entry = WaterEntry(
                **schema.model_dump(),
                user_id=user_id,
                goal_water_volume=self._goal_water_volume,
                date_field=curr_date,
            )

        return await self._water_entry_repository.save(session, waters_entry)
