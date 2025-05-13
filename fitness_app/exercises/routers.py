from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Path, Query, status

from fitness_app.auth.dependencies import AuthenticateUser, HasPermission
from fitness_app.auth.permissions import Authenticated
from fitness_app.core.dependencies import (
    DbSession,
    ExerciseServiceDep,
    FileEntityServiceDep,
)
from fitness_app.core.utils import PageField, SizeField
from fitness_app.exercises.models import Exercise
from fitness_app.exercises.schemas import (
    Difficulty,
    ExerciseCreateSchema,
    ExerciseFindSchema,
    ExerciseSchema,
    ExerciseType,
    ExerciseUpdateSchema,
)


async def exercise_to_schema(
    session: DbSession, file_service: FileEntityServiceDep, exercise: Exercise
) -> ExerciseSchema:

    for photo in exercise.photos:
        photo.full_url = await file_service.get_by_filename(session, photo.filename)
    return exercise


def get_exercise_find_schema(
    name: Optional[str] = Query(None),
    muscle: Optional[str] = Query(None),
    additionalMuscle: Optional[str] = Query(None),
    type: Optional[ExerciseType] = Query(None),
    equipment: Optional[str] = Query(None),
    difficulty: Optional[Difficulty] = Query(None),
    description: Optional[str] = Query(None),
) -> ExerciseFindSchema:
    return ExerciseFindSchema(
        name=name,
        muscle=muscle,
        additionalMuscle=additionalMuscle,
        type=type,
        equipment=equipment,
        difficulty=difficulty,
        description=description,
    )


exercises_router = APIRouter(prefix="/exercises", tags=["Упражнения"])


@exercises_router.post(
    "",
    response_model=ExerciseSchema,
    summary="Создание задания",
    dependencies=[Depends(HasPermission(Authenticated()))],
)
async def create(
    session: DbSession,
    service: ExerciseServiceDep,
    file_service: FileEntityServiceDep,
    user: AuthenticateUser,
    schema: ExerciseCreateSchema,
) -> ExerciseSchema:
    exercise = await service.create(session, schema, user.id)
    return await exercise_to_schema(session, file_service, exercise)


@exercises_router.get(
    "/{id}",
    response_model=ExerciseSchema,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Упражнения с указанным id не найдено"
        }
    },
    summary="Получение задания по id",
    dependencies=[Depends(HasPermission(Authenticated()))],
)
async def get_by_id(
    session: DbSession,
    service: ExerciseServiceDep,
    file_service: FileEntityServiceDep,
    id: Annotated[int, Path],
) -> ExerciseSchema:
    exercise = await service.get_by_id(session, id)
    return await exercise_to_schema(session, file_service, exercise)


@exercises_router.get(
    "/users/current",
    response_model=list[ExerciseSchema],
    summary="Получение заданий пользователя по user_id",
    dependencies=[Depends(HasPermission(Authenticated()))],
)
async def get_by_user_id(
    session: DbSession,
    service: ExerciseServiceDep,
    file_service: FileEntityServiceDep,
    user: AuthenticateUser,
    find_schema: Optional[ExerciseFindSchema] = Depends(get_exercise_find_schema),
    page: PageField = 0,
    size: SizeField = 10,
) -> list[ExerciseSchema]:
    exercises = await service.get_by_user_id(session, user.id, find_schema, page, size)
    exercises_schema = [
        await exercise_to_schema(session, file_service, exercise)
        for exercise in exercises
    ]
    return exercises_schema


@exercises_router.put(
    "",
    summary="Обновить задание",
    response_model=ExerciseSchema,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "Можно изменять только свои упражнения"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Упражнения с указанным id не найдено"
        },
    },
    dependencies=[Depends(HasPermission(Authenticated()))],
)
async def update_by_id(
    session: DbSession,
    service: ExerciseServiceDep,
    file_service: FileEntityServiceDep,
    user: AuthenticateUser,
    schema: ExerciseUpdateSchema,
) -> ExerciseSchema:
    exercise = await service.update_by_id(session, user.id, schema)
    return await exercise_to_schema(session, file_service, exercise)


@exercises_router.delete(
    "/{id}",
    summary="Удаление задания по id",
    response_model=str,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "Можно изменять только свои упражнения"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Упражнения с указанным id не найдено"
        },
    },
    dependencies=[Depends(HasPermission(Authenticated()))],
)
async def delete_by_id(
    session: DbSession,
    service: ExerciseServiceDep,
    user: AuthenticateUser,
    id: Annotated[int, Path],
) -> str:
    await service.delete_by_id(session, user.id, id)
    return "OK"
