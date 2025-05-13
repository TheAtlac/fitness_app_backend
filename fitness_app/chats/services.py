from sqlalchemy.ext.asyncio import AsyncSession

from fitness_app.chats.models import Chat
from fitness_app.chats.repositories import ChatRepository
from fitness_app.chats.schemas import ChatCreateSchema, ChatSchema, ChatType
from fitness_app.core.exceptions import (
    BadRequestException,
    EntityNotFoundException,
    ForbiddenException,
)
from fitness_app.core.schemas import PageSchema
from fitness_app.users.models import User
from fitness_app.users.schemas import UserSchema
from fitness_app.users.services import UserService


class ChatService:
    def __init__(
        self,
        chat_repository: ChatRepository,
        user_service: UserService,
    ):
        self._chat_repository = chat_repository
        self._user_service = user_service

    async def create(
        self,
        session: AsyncSession,
        users: list,
        type: ChatType = "DIALOGUE",
    ):
        if not await self._chat_repository.is_exist_by_users(
            session, users[0], users[1]
        ):
            chat_create_schema = ChatCreateSchema(type=type)
            chat = Chat(**chat_create_schema.model_dump())
            chat.users = users
            chat.messages = []

            return await self._chat_repository.save(session, chat)
        return await self.get_by_user_id(session, users[0], users[1].id)

    async def create_new(
        self,
        session: AsyncSession,
        users: list,
        type: ChatType = ChatType.WORKOUT,
    ):
        chat_create_schema = ChatCreateSchema(type=type)
        chat = Chat(**chat_create_schema.model_dump())
        chat.users = users
        chat.messages = []

        return await self._chat_repository.save(session, chat)

    async def get_by_chat_id(
        self,
        session: AsyncSession,
        user: User,
        chat_id: int,
    ):
        chat = await self._chat_repository.get_with_users_by_chat_id(session, chat_id)
        if chat is None:
            raise EntityNotFoundException("Chat with given id was not found")
        if user not in chat.users:
            raise ForbiddenException("Authenticated user is not a member of this chat")

        return chat

    async def get_by_user_id(self, session: AsyncSession, user: User, user_id: int):
        if user.id == user_id:
            raise BadRequestException("Given user id equals to authorized uzer")
        user2 = await self._user_service.get_by_id(session, user_id)
        chat = await self._chat_repository.get_with_users_by_users(session, user, user2)
        if chat is None:
            raise EntityNotFoundException("Chat with given user was not found")

        return chat

    async def is_accessed_chat(self, session: AsyncSession, user: User, chat_id: int):
        chat = await self._chat_repository.get_with_users_by_chat_id(session, chat_id)
        if chat is None:
            raise EntityNotFoundException("Chat with given id was not found")
        if user not in chat.users:
            raise ForbiddenException("Authenticated user is not a member of this chat")

        return True

    async def get_chats_by_user(
        self,
        session: AsyncSession,
        user: User,
        page: int,
        size: int,
    ):
        total_chats_count = await self._chat_repository.count_chats(session, user.id)
        chats = await self._chat_repository.get_chats(session, user.id, page, size)
        chat_dicts = [chat.__dict__ for chat in chats]
        for chat_dict in chat_dicts:
            chat_dict["users"] = [
                UserSchema.model_validate(user) for user in chat_dict["users"]
            ]
        return PageSchema(total_items_count=total_chats_count, items=chat_dicts)

    async def delete_by_id(
        self, session: AsyncSession, user: User, chat_id: int
    ) -> ChatSchema:
        chat = await self.get_by_chat_id(session, user, chat_id)
        schema = ChatSchema(**chat.__dict__)

        await self._chat_repository.delete(session, chat)
        return schema
