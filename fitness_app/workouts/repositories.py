from typing import Optional

from sqlalchemy import and_, null, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from fitness_app.chats.models import Chat
from fitness_app.exercises.models import Exercise
from fitness_app.workouts.models import ExerciseWorkout, Workout
from fitness_app.workouts.schemas import WorkoutFindSchema


class WorkoutRepository:
    async def save(self, session: AsyncSession, workout: Workout):
        session.add(workout)
        await session.flush()
        await session.commit()
        return workout

    async def get_by_id(self, session: AsyncSession, id: int):
        statement = (
            select(Workout)
            .where(Workout.id == id)
            .options(
                joinedload(Workout.customer),
                joinedload(Workout.coach),
                joinedload(Workout.chat).options(selectinload(Chat.users)),
                selectinload(Workout.exercise_workouts).options(
                    joinedload(ExerciseWorkout.exercise).options(
                        selectinload(Exercise.photos)
                    ),
                    joinedload(ExerciseWorkout.workout),
                ),
            )
        )

        result = await session.execute(statement)
        workout = result.scalar_one_or_none()
        if workout and workout.exercise_workouts:
            workout.exercise_workouts.sort(key=lambda workout: workout.num_order)
        return workout

    async def get_workouts_by_coach_id_or_customer_id(
        self,
        session: AsyncSession,
        coach_id: Optional[int],
        customer_id: Optional[int],
        find_schema: Optional[WorkoutFindSchema],
        page: int,
        size: int,
    ):
        statement = select(Workout)

        if coach_id:
            statement = statement.where(
                or_(
                    and_(Workout.coach_id == coach_id, Workout.customer_id == null()),
                    and_(Workout.coach_id == null(), Workout.customer_id == null()),
                )
            )
        elif customer_id:
            statement = statement.where(
                and_(Workout.coach_id.isnot(None), Workout.customer_id == customer_id)
            )

        if find_schema:
            if find_schema.name:
                statement = statement.where(Workout.name.icontains(find_schema.name))
            if find_schema.type_connection:
                statement = statement.where(
                    Workout.type_connection.icontains(find_schema.type_connection)
                )
            if find_schema.from_time_start:
                statement = statement.where(
                    Workout.time_start >= find_schema.from_time_start
                )
            if find_schema.to_time_start:
                statement = statement.where(
                    Workout.time_start <= find_schema.to_time_start
                )

        statement = (
            statement.offset(page * size)
            .limit(size)
            .order_by(Workout.time_start)
            .options(
                joinedload(Workout.customer),
                joinedload(Workout.coach),
                joinedload(Workout.chat).options(selectinload(Chat.users)),
                selectinload(Workout.exercise_workouts).options(
                    joinedload(ExerciseWorkout.exercise).options(
                        selectinload(Exercise.photos)
                    ),
                    joinedload(ExerciseWorkout.workout),
                ),
            )
        )

        result = await session.execute(statement)
        workouts = result.scalars().all()
        for workout in workouts:
            if workout.exercise_workouts:
                workout.exercise_workouts.sort(key=lambda workout: workout.num_order)

        return workouts

    async def update(self, session: AsyncSession, workout: Workout):
        session.add(workout)
        await session.flush()
        await session.commit()
        await session.refresh(workout)
        return workout

    async def delete(self, session: AsyncSession, workout: Workout):
        await session.delete(workout)
        await session.commit()
        return workout


class ExerciseWorkoutRepository:
    async def save(self, session: AsyncSession, exercise_workout: ExerciseWorkout):
        session.add(exercise_workout)
        await session.flush()
        await session.commit()
        return exercise_workout

    async def get_by_id(self, session: AsyncSession, id: int):
        statement = (
            select(ExerciseWorkout)
            .where(ExerciseWorkout.id == id)
            .options(
                joinedload(ExerciseWorkout.exercise).options(
                    selectinload(Exercise.photos)
                ),
                joinedload(ExerciseWorkout.workout),
            )
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def update(self, session: AsyncSession, exercise_workout: ExerciseWorkout):
        session.add(exercise_workout)
        await session.flush()
        await session.commit()
        await session.refresh(exercise_workout)
        return exercise_workout

    async def delete(self, session: AsyncSession, exercise_workout: ExerciseWorkout):
        await session.delete(exercise_workout)
        await session.commit()
        return exercise_workout
