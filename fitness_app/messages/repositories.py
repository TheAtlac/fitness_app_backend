from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from fitness_app.messages.models import Message


class MessageRepository:

    async def save(self, session: AsyncSession, message: Message):
        session.add(message)
        await session.flush()
        await session.commit()
        return message

    async def delete(self, session: AsyncSession, message: Message):
        await session.delete(message)
        await session.commit()
        return message

    async def count_messages(
        self,
        session: AsyncSession,
        chat_id: int,
    ):
        statement = select(func.count(Message.id)).where(Message.chat_id == chat_id)
        result = await session.execute(statement)
        return result.scalar_one()

    async def get_messagees(
        self,
        session: AsyncSession,
        chat_id: int,
        page: int,
        size: int,
    ):
        statement = (
            select(Message)
            .where(Message.chat_id == chat_id)
            .order_by(Message.timestamp.desc())
            .offset(page * size)
            .limit(size)
        )
        result = await session.execute(statement)
        return result.scalars().all()
