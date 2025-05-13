from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from fitness_app.core.utils import update_model_by_schema
from fitness_app.steps.models import StepsEntry
from fitness_app.steps.repositories import StepsRepository
from fitness_app.steps.schemas import StepsCreateSchema


class StepsService:
    def __init__(self, steps_repository: StepsRepository, goal_steps: int):
        self._steps_repository = steps_repository
        self._goal_steps = goal_steps

    async def get_by_dates(
        self, session: AsyncSession, user_id: int, date_start: date, date_finish: date
    ):

        steps = await self._steps_repository.get_by_dates(
            session, user_id, date_start, date_finish
        )

        return steps

    async def create_or_update(
        self, session: AsyncSession, user_id: int, schema: StepsCreateSchema
    ):
        curr_date = date.today()
        if await self._steps_repository.exists_by_user_id_and_date(
            session, user_id, curr_date
        ):
            steps_entry = await self._steps_repository.get_by_user_id_and_date(
                session, user_id, curr_date
            )
            update_model_by_schema(steps_entry, schema)
        else:
            steps_entry = StepsEntry(
                **schema.model_dump(),
                user_id=user_id,
                goal_steps=self._goal_steps,
                date_field=curr_date,
            )

        return await self._steps_repository.save(session, steps_entry)
