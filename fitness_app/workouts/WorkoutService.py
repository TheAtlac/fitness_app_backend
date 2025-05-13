from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from fitness_app.chats.schemas import ChatType
from fitness_app.chats.services import ChatService
from fitness_app.coaches.services import CoachService
from fitness_app.core.exceptions import (
    BadRequestException,
    EntityNotFoundException,
    ForbiddenException,
)
from fitness_app.core.utils import update_model_by_schema
from fitness_app.customers.services import CustomerService
from fitness_app.exercises.services import ExerciseService
from fitness_app.users.models import User
from fitness_app.users.schemas import Role
from fitness_app.users.services import UserService
from fitness_app.workouts.models import ExerciseWorkout, Workout
from fitness_app.workouts.repositories import (
    ExerciseWorkoutRepository,
    WorkoutRepository,
)
from fitness_app.workouts.schemas import (
    WorkoutCreateSchema,
    WorkoutFindSchema,
    WorkoutUpdateSchema,
)


class WorkoutService:
    def __init__(
        self,
        workout_repository: WorkoutRepository,
        exercise_workout_repository: ExerciseWorkoutRepository,
        exercise_service: ExerciseService,
        chat_service: ChatService,
        coach_service: CoachService,
        customer_service: CustomerService,
        user_service: UserService,
    ):
        self._workout_repository = workout_repository
        self._exercise_workout_repository = exercise_workout_repository
        self._exercise_service = exercise_service
        self._chat_service = chat_service
        self._coach_service = coach_service
        self._customer_service = customer_service
        self._user_service = user_service

    async def create(
        self,
        session: AsyncSession,
        user: User,
        schema: WorkoutCreateSchema,
    ):
        if not schema.coach_id and not schema.customer_id:
            raise BadRequestException(
                "Необходимо указать coach_id или customer_id или вместе"
            )

        if (user.role == Role.COACH and user.coach_info.id != schema.coach_id) or (
            user.role == Role.CUSTOMER and user.customer_info.id != schema.customer_id
        ):
            raise ForbiddenException("Необходимо указать свой coach_id или customer_id")

        workout = Workout(**schema.model_dump(exclude=["exercise_workouts_create"]))
        workout.exercise_workouts = []

        if schema.coach_id:
            workout.coach = await self._coach_service.get_by_id(
                session, schema.coach_id
            )

        if schema.customer_id:
            workout.customer = await self._customer_service.get_by_id(
                session, schema.customer_id
            )

        if schema.coach_id and schema.customer_id:
            users = [workout.coach.user, workout.customer.user]
            workout.chat = await self._chat_service.create_new(
                session, users, ChatType.WORKOUT
            )
            workout.chat_id = workout.chat.id

        workout = await self._workout_repository.save(session, workout)

        if schema.exercise_workouts_create:
            for exercise_workout_schema in schema.exercise_workouts_create:

                exercise_workout = ExerciseWorkout(
                    **exercise_workout_schema.model_dump()
                )
                exercise_workout.workout_id = workout.id

                exercise_workout.exercise = await self._exercise_service.get_by_id(
                    session, exercise_workout_schema.exercise_id
                )

                workout.exercise_workouts.append(
                    await self._exercise_workout_repository.save(
                        session, exercise_workout
                    )
                )

        return await self._workout_repository.save(session, workout)

    async def get_by_id(self, session: AsyncSession, id: int):
        workout = await self._workout_repository.get_by_id(session, id)

        if not workout:
            raise EntityNotFoundException("Тренировки с указанным id не найдено")

        return workout

    async def get_workouts_by_user_id(
        self,
        session: AsyncSession,
        user_id: int,
        find_schema: Optional[WorkoutFindSchema],
        page: int,
        size: int,
    ):
        user = await self._user_service.get_by_id(session, user_id)

        if user.role == Role.COACH:
            return (
                await self._workout_repository.get_workouts_by_coach_id_or_customer_id(
                    session=session,
                    coach_id=user.coach_info.id,
                    customer_id=None,
                    find_schema=find_schema,
                    page=page,
                    size=size,
                )
            )
        elif user.role == Role.CUSTOMER:
            return (
                await self._workout_repository.get_workouts_by_coach_id_or_customer_id(
                    session=session,
                    coach_id=None,
                    customer_id=user.customer_info.id,
                    find_schema=find_schema,
                    page=page,
                    size=size,
                )
            )

    async def update_by_id(
        self,
        session: AsyncSession,
        user: User,
        schema: WorkoutUpdateSchema,
    ):
        workout = await self._workout_repository.get_by_id(session, schema.id)

        if not workout:
            raise EntityNotFoundException("Тренировки с указанным id не найдено")

        if (user.role == Role.COACH and user.coach_info.id != workout.coach_id) or (
            user.role == Role.CUSTOMER and user.customer_info.id != workout.customer_id
        ):
            raise ForbiddenException("Нельзя изменять не вашу тренировку")

        update_model_by_schema(workout, schema)
        return await self._workout_repository.update(session, workout)

    async def delete_by_id(self, session: AsyncSession, user: User, id: int):
        workout = await self._workout_repository.get_by_id(session, id)

        if not workout:
            raise EntityNotFoundException("Тренировки с указанным id не найдено")

        if (user.role == Role.COACH and user.coach_info.id != workout.coach_id) or (
            user.role == Role.CUSTOMER and user.customer_info.id != workout.customer_id
        ):
            raise ForbiddenException("Нельзя изменять не вашу тренировку")

        if workout.chat_id:
            await self._chat_service.delete_by_id(session, user, workout.chat_id)

        return await self._workout_repository.delete(session, workout)
