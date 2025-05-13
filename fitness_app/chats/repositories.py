from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from fitness_app.chats.models import Chat, ChatsUsers
from fitness_app.users.models import User


class ChatRepository:

    async def save(self, session: AsyncSession, chat: Chat):
        session.add(chat)
        await session.flush()
        await session.commit()
        return chat

    async def delete(self, session: AsyncSession, chat: Chat):
        await session.delete(chat)
        await session.commit()
        return chat

    async def get_with_users_by_chat_id(
        self, session: AsyncSession, chat_id: int
    ) -> Chat:
        statement = (
            select(Chat).where(Chat.id == chat_id).options(selectinload(Chat.users))
        )
        result = await session.execute(statement)
        return result.scalar_one_or_none()

    async def is_exist_by_users(
        self, session: AsyncSession, user1: User, user2: User
    ) -> Chat:
        subquery1 = select(ChatsUsers.chat_id).where(ChatsUsers.user_id == user1.id)
        subquery2 = select(ChatsUsers.chat_id).where(ChatsUsers.user_id == user2.id)
        statement = (
            select(Chat)
            .where(Chat.id.in_(subquery1))
            .where(Chat.id.in_(subquery2))
            .where(Chat.type == "DIALOGUE")
        )
        result = await session.execute(statement)
        chat = result.scalar_one_or_none()
        return chat is not None

    async def get_with_users_by_users(
        self, session: AsyncSession, user1: User, user2: User
    ) -> Chat:
        subquery1 = select(ChatsUsers.chat_id).where(ChatsUsers.user_id == user1.id)
        subquery2 = select(ChatsUsers.chat_id).where(ChatsUsers.user_id == user2.id)
        statement = (
            select(Chat)
            .where(Chat.id.in_(subquery1))
            .where(Chat.id.in_(subquery2))
            .where(Chat.type == "DIALOGUE")
            .options(selectinload(Chat.users))
        )
        result = await session.execute(statement)

        return result.scalar_one_or_none()

    async def count_chats(
        self,
        session: AsyncSession,
        user_id: int,
    ):
        statement = (
            select(func.count(Chat.id))
            .select_from(User)
            .join(User.chats)
            .where(User.id == user_id)
            .where(Chat.type == "DIALOGUE")
        )
        result = await session.execute(statement)
        return result.scalar_one()

    async def get_chats(
        self,
        session: AsyncSession,
        user_id: int,
        page: int,
        size: int,
    ):
        statement = (
            select(Chat)
            .join(Chat.users)
            .where(User.id == user_id)
            .where(Chat.type == "DIALOGUE")
            .order_by(Chat.last_timestamp.desc())
            .offset(page * size)
            .limit(size)
            .options(joinedload(Chat.users))
        )
        result = await session.execute(statement)
        return result.unique().scalars().all()
