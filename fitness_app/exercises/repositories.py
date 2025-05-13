from typing import Optional

from sqlalchemy import desc, null, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from fitness_app.exercises.models import Exercise
from fitness_app.exercises.schemas import ExerciseFindSchema


class ExerciseRepository:
    async def save(self, session: AsyncSession, exercise: Exercise):
        session.add(exercise)
        await session.flush()
        await session.commit()
        return exercise

    async def get_by_id(self, session: AsyncSession, id: int):
        statement = (
            select(Exercise)
            .where(Exercise.id == id)
            .options(selectinload(Exercise.photos))
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_user_id(
        self,
        session: AsyncSession,
        user_id: int,
        find_schema: Optional[ExerciseFindSchema],
        page: int,
        size: int,
    ):
        statement = select(Exercise).where(
            or_(Exercise.user_id == null(), Exercise.user_id == user_id)
        )
        if find_schema:
            if find_schema.name:
                statement = statement.where(Exercise.name.icontains(find_schema.name))
            if find_schema.muscle:
                statement = statement.where(
                    Exercise.muscle.icontains(find_schema.muscle)
                )
            if find_schema.additionalMuscle:
                statement = statement.where(
                    Exercise.additionalMuscle.icontains(find_schema.additionalMuscle)
                )
            if find_schema.type:
                statement = statement.where(Exercise.type == find_schema.type)
            if find_schema.equipment:
                statement = statement.where(
                    Exercise.equipment.icontains(find_schema.equipment)
                )
            if find_schema.difficulty:
                statement = statement.where(
                    Exercise.difficulty == find_schema.difficulty
                )
            if find_schema.description:
                statement = statement.where(
                    Exercise.description.icontains(find_schema.description)
                )
        statement = (
            statement.offset(page * size)
            .limit(size)
            .order_by(desc(Exercise.id))
            .options(selectinload(Exercise.photos))
        )

        result = await session.execute(statement)
        return result.scalars().all()

    async def delete(self, session: AsyncSession, exercise: Exercise):
        await session.delete(exercise)
        await session.commit()
        return exercise
