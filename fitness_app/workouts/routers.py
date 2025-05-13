from datetime import datetime
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Path, Query, status

from fitness_app.auth.dependencies import AuthenticateUser, HasPermission
from fitness_app.auth.permissions import Authenticated
from fitness_app.core.dependencies import (
    DbSession,
    ExerciseWorkoutServiceDep,
    FileEntityServiceDep,
    WorkoutServiceDep,
)
from fitness_app.core.utils import PageField, SizeField
from fitness_app.workouts.models import ExerciseWorkout, Workout
from fitness_app.workouts.schemas import (
    ExerciseWorkoutCreateSchema,
    ExerciseWorkoutSchema,
    ExerciseWorkoutUpdateSchema,
    TypeConnection,
    WorkoutCreateSchema,
    WorkoutFindSchema,
    WorkoutSchema,
    WorkoutUpdateSchema,
)


async def exercise_workout_to_schema(
    session: DbSession,
    file_service: FileEntityServiceDep,
    exercise_workout: ExerciseWorkout,
) -> ExerciseWorkout:

    for photo in exercise_workout.exercise.photos:
        photo.full_url = await file_service.get_by_filename(session, photo.filename)

    return exercise_workout


async def workout_to_schema(
    session: DbSession, file_service: FileEntityServiceDep, workout: Workout
) -> WorkoutSchema:

    for exercise_workout in workout.exercise_workouts:
        exercise_workout = await exercise_workout_to_schema(
            session, file_service, exercise_workout
        )

    return workout


def get_workout_find_schema(
    name: Optional[str] = Query(None),
    type_connection: Optional[TypeConnection] = Query(None),
    from_time_start: Optional[datetime] = Query(None),
    to_time_start: Optional[datetime] = Query(None),
) -> WorkoutFindSchema:
    return WorkoutFindSchema(
        name=name,
        type_connection=type_connection,
        from_time_start=from_time_start,
        to_time_start=to_time_start,
    )


workouts_router = APIRouter(prefix="/workouts", tags=["Тренировки"])


@workouts_router.post(
    "",
    response_model=WorkoutSchema,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "Необходимо указать свой coach_id или customer_id"
        }
    },
    summary="Создание тренировки",
    dependencies=[Depends(HasPermission(Authenticated()))],
)
async def create(
    session: DbSession,
    service: WorkoutServiceDep,
    file_service: FileEntityServiceDep,
    user: AuthenticateUser,
    schema: WorkoutCreateSchema,
) -> WorkoutSchema:
    workout = await service.create(session, user, schema)
    return await workout_to_schema(session, file_service, workout)


@workouts_router.get(
    "/{id}",
    response_model=WorkoutSchema,
    responses={
        status.HTTP_404_NOT_FOUND: {
            "description": "Тренировки с указанным id не найдено"
        }
    },
    summary="Получение тренировки по id",
    dependencies=[Depends(HasPermission(Authenticated()))],
)
async def get_by_id(
    session: DbSession,
    service: WorkoutServiceDep,
    file_service: FileEntityServiceDep,
    id: Annotated[int, Path],
) -> WorkoutSchema:
    workout = await service.get_by_id(session, id)
    return await workout_to_schema(session, file_service, workout)


@workouts_router.get(
    "/users/{user_id}",
    response_model=list[WorkoutSchema],
    summary="Получить список тренировок по user_id",
    dependencies=[Depends(HasPermission(Authenticated()))],
)
async def get_workouts_by_user_id(
    session: DbSession,
    service: WorkoutServiceDep,
    file_service: FileEntityServiceDep,
    user_id: Annotated[int, Path],
    find_schema: Optional[WorkoutFindSchema] = Depends(get_workout_find_schema),
    page: PageField = 0,
    size: SizeField = 10,
) -> list[WorkoutSchema]:
    workouts = await service.get_workouts_by_user_id(
        session, user_id, find_schema, page, size
    )
    workouts_schema = [
        await workout_to_schema(session, file_service, workout) for workout in workouts
    ]
    return workouts_schema


@workouts_router.get(
    "/users/get/me",
    response_model=list[WorkoutSchema],
    summary="Получить список тренировок текущего пользователя",
    dependencies=[Depends(HasPermission(Authenticated()))],
)
async def get_workouts_by_current_user(
    session: DbSession,
    service: WorkoutServiceDep,
    file_service: FileEntityServiceDep,
    user: AuthenticateUser,
    find_schema: Optional[WorkoutFindSchema] = Depends(get_workout_find_schema),
    page: PageField = 0,
    size: SizeField = 10,
) -> list[WorkoutSchema]:
    workouts = await service.get_workouts_by_user_id(
        session, user.id, find_schema, page, size
    )
    workouts_schema = [
        await workout_to_schema(session, file_service, workout) for workout in workouts
    ]
    return workouts_schema


@workouts_router.put(
    "",
    summary="Обновить тренировку по id",
    response_model=WorkoutSchema,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "Нельзя изменять не вашу тренировку"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Тренировки с указанным id не найдено"
        },
    },
    dependencies=[Depends(HasPermission(Authenticated()))],
)
async def update_by_id(
    session: DbSession,
    user: AuthenticateUser,
    service: WorkoutServiceDep,
    file_service: FileEntityServiceDep,
    schema: WorkoutUpdateSchema,
) -> WorkoutSchema:

    workout = await service.update_by_id(session, user, schema)
    return await workout_to_schema(session, file_service, workout)


@workouts_router.delete(
    "/{id}",
    summary="Удаление тренировки по id",
    response_model=str,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "Нельзя изменять не вашу тренировку"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Тренировки с указанным id не найдено"
        },
    },
    dependencies=[Depends(HasPermission(Authenticated()))],
)
async def delete_by_id(
    session: DbSession,
    user: AuthenticateUser,
    service: WorkoutServiceDep,
    file_service: FileEntityServiceDep,
    id: Annotated[int, Path],
) -> str:

    await service.delete_by_id(session, user, id)
    return "OK"


@workouts_router.post(
    "/exercises",
    response_model=ExerciseWorkoutSchema,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "Необходимо указать свой coach_id или customer_id"
        },
    },
    summary="Создание упражнения для тренировки",
    dependencies=[Depends(HasPermission(Authenticated()))],
)
async def create_exercise_workout(
    session: DbSession,
    service: ExerciseWorkoutServiceDep,
    file_service: FileEntityServiceDep,
    user: AuthenticateUser,
    schema: ExerciseWorkoutCreateSchema,
) -> ExerciseWorkoutSchema:

    exercise_workout = await service.create(session, user, schema)
    return await exercise_workout_to_schema(session, file_service, exercise_workout)


@workouts_router.put(
    "/exercises/{exercise_workout_id}",
    summary="Обновить упражнение для тренировки по id",
    response_model=ExerciseWorkoutSchema,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "Нельзя изменять не вашу тренировку"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Упражнения для тренировки с указанным id не найдено"
        },
    },
    dependencies=[Depends(HasPermission(Authenticated()))],
)
async def update_exercise_workout_by_id(
    session: DbSession,
    user: AuthenticateUser,
    service: ExerciseWorkoutServiceDep,
    file_service: FileEntityServiceDep,
    schema: ExerciseWorkoutUpdateSchema,
) -> ExerciseWorkoutSchema:

    exercise_workout = await service.update_by_id(session, user, schema)
    return await exercise_workout_to_schema(session, file_service, exercise_workout)


@workouts_router.delete(
    "/exercises/{exercise_workout_id}",
    summary="Удаление задания для тренировки по id",
    response_model=str,
    responses={
        status.HTTP_403_FORBIDDEN: {
            "description": "Нельзя изменять не вашу тренировку"
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Упражнения для тренировки с указанным id не найдено"
        },
    },
    dependencies=[Depends(HasPermission(Authenticated()))],
)
async def delete_exercise_workout_by_id(
    session: DbSession,
    user: AuthenticateUser,
    service: ExerciseWorkoutServiceDep,
    file_service: FileEntityServiceDep,
    exercise_workout_id: Annotated[int, Path],
) -> str:

    await service.delete_by_id(session, user, exercise_workout_id)
    return "OK"
