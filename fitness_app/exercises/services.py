from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from fitness_app.core.exceptions import (
    BadRequestException,
    EntityNotFoundException,
    ForbiddenException,
)
from fitness_app.core.utils import update_model_by_schema
from fitness_app.exercises.models import Exercise
from fitness_app.exercises.repositories import ExerciseRepository
from fitness_app.exercises.schemas import (
    ExerciseCreateSchema,
    ExerciseFindSchema,
    ExerciseUpdateSchema,
)
from fitness_app.file_entities.services import FileEntityService


class ExerciseService:
    def __init__(
        self,
        exercise_repository: ExerciseRepository,
        file_entity_service: FileEntityService,
    ):
        self._exercise_repository = exercise_repository
        self._file_entity_service = file_entity_service

    async def create(
        self,
        session: AsyncSession,
        schema: ExerciseCreateSchema,
        user_id: int,
    ):
        exercise = Exercise(**schema.model_dump(exclude=["photo_ids"]))
        exercise.user_id = user_id
        exercise.photos = []

        if schema.photo_ids:
            for photo_id in schema.photo_ids:

                photo_entity = await self._file_entity_service.get_by_id(
                    session, photo_id
                )
                if photo_entity.exercise_id:
                    raise BadRequestException(
                        "Photo entity with given id already have entity_id"
                    )
                else:
                    exercise.photos.append(photo_entity)

        return await self._exercise_repository.save(session, exercise)

    async def get_by_id(self, session: AsyncSession, id: int):
        exercise = await self._exercise_repository.get_by_id(session, id)
        if not exercise:
            raise EntityNotFoundException("Упражнения с указанным id не найдено")

        return exercise

    async def get_by_user_id(
        self,
        session: AsyncSession,
        user_id: int,
        find_schema: Optional[ExerciseFindSchema],
        page: int,
        size: int,
    ):
        return await self._exercise_repository.get_by_user_id(
            session, user_id, find_schema, page, size
        )

    async def update_by_id(
        self,
        session: AsyncSession,
        user_id: int,
        schema: ExerciseUpdateSchema,
    ):
        exercise = await self._exercise_repository.get_by_id(session, schema.id)
        if not exercise:
            raise EntityNotFoundException("Упражнения с указанным id не найдено")
        if not exercise.user_id:
            raise ForbiddenException("Отказано в доступе")
        if exercise.user_id != user_id:
            raise ForbiddenException("Можно изменять только свои упражнения")

        update_model_by_schema(exercise, schema)
        exercise = await self._exercise_repository.save(session, exercise)

        if schema.photo_ids or schema.photo_ids == []:
            existing_set = set(photo.id for photo in exercise.photos)
            new_set = set(schema.photo_ids)

            set_ids_to_delete = existing_set - new_set
            set_ids_to_add = new_set - existing_set

            for photo_id in set_ids_to_delete:
                await self._file_entity_service.delete_by_id(session, photo_id)
            for photo_id in set_ids_to_add:
                await self._file_entity_service.add_exercise_id_by_id(
                    session, exercise.id, photo_id
                )

        await session.refresh(exercise)
        return await self._exercise_repository.get_by_id(session, exercise.id)

    async def delete_by_id(self, session: AsyncSession, user_id: int, id: int):
        exercise = await self._exercise_repository.get_by_id(session, id)

        if not exercise:
            raise EntityNotFoundException("Упражнения с указанным id не найдено")
        if not exercise.user_id:
            raise ForbiddenException("Отказано в доступе")
        if exercise.user_id != user_id:
            raise ForbiddenException("Можно изменять только свои упражнения")

        if exercise.photos:
            for i in range(len(exercise.photos)):
                await self._file_entity_service.delete_by_id(
                    session, exercise.photos[i].id
                )

        return await self._exercise_repository.delete(session, exercise)
