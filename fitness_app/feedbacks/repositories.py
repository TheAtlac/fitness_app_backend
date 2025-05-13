from sqlalchemy import and_, exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from fitness_app.feedbacks.models import Feedback


class FeedbackRepository:

    async def save(self, session: AsyncSession, feedback: Feedback):
        session.add(feedback)
        await session.flush()
        await session.commit()
        return feedback

    async def delete(self, session: AsyncSession, feedback: Feedback):
        await session.delete(feedback)
        await session.commit()
        return feedback

    async def is_exists(self, session: AsyncSession, coach_id: int, customer_id: int):
        statement = select(
            exists().where(
                (
                    and_(
                        Feedback.coach_id == coach_id,
                        Feedback.customer_id == customer_id,
                    )
                )
            )
        )
        result = await session.execute(statement)
        return result.scalar()

    async def get_by_ids(self, session: AsyncSession, coach_id: int, customer_id: int):
        statement = select(Feedback).where(
            and_(
                Feedback.coach_id == coach_id,
                Feedback.customer_id == customer_id,
            )
        )

        result = await session.execute(statement)
        return result.scalar_one()
