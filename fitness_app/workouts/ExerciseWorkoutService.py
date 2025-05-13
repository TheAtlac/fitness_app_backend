from sqlalchemy.ext.asyncio import AsyncSession

from fitness_app.core.exceptions import EntityNotFoundException, ForbiddenException
from fitness_app.core.utils import update_model_by_schema
from fitness_app.exercises.services import ExerciseService
from fitness_app.users.models import User
from fitness_app.users.schemas import Role
from fitness_app.workouts.models import ExerciseWorkout
from fitness_app.workouts.repositories import ExerciseWorkoutRepository
from fitness_app.workouts.schemas import (
    ExerciseWorkoutCreateSchema,
    ExerciseWorkoutUpdateSchema,
)
from fitness_app.workouts.WorkoutService import WorkoutService


class ExerciseWorkoutService:
    def __init__(
        self,
        workout_service: WorkoutService,
        exercise_workout_repository: ExerciseWorkoutRepository,
        exercise_service: ExerciseService,
    ):
        self._workout_service = workout_service
        self._exercise_workout_repository = exercise_workout_repository
        self._exercise_service = exercise_service

    async def create(
        self,
        session: AsyncSession,
        user: User,
        schema: ExerciseWorkoutCreateSchema,
    ):
        exercise_workout = ExerciseWorkout(**schema.model_dump())

        workout = await self._workout_service.get_by_id(session, schema.workout_id)
        if (user.role == Role.COACH and user.coach_info.id != workout.coach_id) or (
            user.role == Role.CUSTOMER and user.customer_info.id != workout.customer_id
        ):
            raise ForbiddenException("Необходимо указать свой coach_id или customer_id")

        exercise_workout.exercise = await self._exercise_service.get_by_id(
            session, schema.exercise_id
        )

        return await self._exercise_workout_repository.save(session, exercise_workout)

    async def update_by_id(
        self,
        session: AsyncSession,
        user: User,
        schema: ExerciseWorkoutUpdateSchema,
    ):
        exercise_workout = await self._exercise_workout_repository.get_by_id(
            session, schema.id
        )

        if not exercise_workout:
            raise EntityNotFoundException(
                "Упражнения для тренировки с указанным id не найдено"
            )

        if not exercise_workout.workout:
            raise EntityNotFoundException("Тренировки с указанным id не найдено")

        if (
            user.role == Role.COACH
            and user.coach_info.id != exercise_workout.workout.coach_id
        ) or (
            user.role == Role.CUSTOMER
            and user.customer_info.id != exercise_workout.workout.customer_id
        ):
            raise ForbiddenException("Нельзя изменять не вашу тренировку")

        update_model_by_schema(exercise_workout, schema)
        exercise_workout.exercise = await self._exercise_service.get_by_id(
            session, schema.exercise_id
        )

        return await self._exercise_workout_repository.update(session, exercise_workout)

    async def delete_by_id(self, session: AsyncSession, user: User, id: int):
        exercise_workout = await self._exercise_workout_repository.get_by_id(
            session, id
        )

        if not exercise_workout:
            raise EntityNotFoundException(
                "Упражнения для тренировки с указанным id не найдено"
            )

        if not exercise_workout.workout:
            raise EntityNotFoundException("Тренировки с указанным id не найдено")

        if (
            user.role == Role.COACH
            and user.coach_info.id != exercise_workout.workout.coach_id
        ) or (
            user.role == Role.CUSTOMER
            and user.customer_info.id != exercise_workout.workout.customer_id
        ):
            raise ForbiddenException("Нельзя изменять не вашу тренировку")

        return await self._exercise_workout_repository.delete(session, exercise_workout)
