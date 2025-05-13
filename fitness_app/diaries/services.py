from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from fitness_app.core.exceptions import BadRequestException
from fitness_app.core.utils import update_model_by_schema
from fitness_app.diaries.models import DiaryEntry
from fitness_app.diaries.repositories import DiaryRepository
from fitness_app.diaries.schemas import DiaryCreateSchema
from fitness_app.file_entities.services import FileEntityService


class DiaryService:
    def __init__(
        self, diary_repository: DiaryRepository, file_entity_service: FileEntityService
    ):
        self._diary_repository = diary_repository
        self._file_entity_service = file_entity_service

    async def get_by_dates(
        self, session: AsyncSession, user_id: int, date_start: date, date_finish: date
    ):
        diaries = await self._diary_repository.get_by_dates(
            session, user_id, date_start, date_finish
        )
        return diaries

    async def create(
        self,
        session: AsyncSession,
        user_id: int,
        schema: DiaryCreateSchema,
        date_field: date,
    ):
        diary = DiaryEntry(
            **schema.model_dump(),
            user_id=user_id,
            date_field=date_field,
        )

        if schema.file_entity_id:
            file_entity = await self._file_entity_service.get_by_id(
                session, schema.file_entity_id
            )
            if file_entity.exercise_id:
                raise BadRequestException("File already belongs to exercise")

            diary.voice_note = file_entity

        return diary

    async def update(
        self,
        session: AsyncSession,
        user_id: int,
        schema: DiaryCreateSchema,
        date_field: date,
    ):
        diary = await self._diary_repository.get_by_user_id_and_date(
            session, user_id=user_id, date_field=date_field
        )

        if diary.file_entity_id != schema.file_entity_id:
            if diary.file_entity_id:
                await self._file_entity_service.delete_by_id(
                    session, diary.file_entity_id
                )

                await session.refresh(diary)

            if schema.file_entity_id:
                file_entity = await self._file_entity_service.get_by_id(
                    session, schema.file_entity_id
                )
                if file_entity.exercise_id:
                    raise BadRequestException("File already belongs to exercise")

                diary.voice_note = file_entity

        update_model_by_schema(diary, schema)

        return diary

    async def create_or_update(
        self, session: AsyncSession, user_id: int, schema: DiaryCreateSchema
    ):
        date_field = date.today()

        if await self._diary_repository.exists_by_user_id_and_date(
            session, user_id, date_field
        ):
            diary = await self.update(session, user_id, schema, date_field)
        else:
            diary = await self.create(session, user_id, schema, date_field)

        return await self._diary_repository.save(session, diary)
