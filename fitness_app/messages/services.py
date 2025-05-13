from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from fitness_app.chats.services import ChatService
from fitness_app.core.exceptions import EntityNotFoundException, ForbiddenException
from fitness_app.core.schemas import PageSchema
from fitness_app.core.utils import update_model_by_schema
from fitness_app.file_entities.services import FileEntityService
from fitness_app.messages.models import Message
from fitness_app.messages.repositories import MessageRepository
from fitness_app.messages.schemas import MessageBaseSchema, MessageCreateSchema
from fitness_app.users.models import User


class MessageService:
    def __init__(
        self,
        message_repository: MessageRepository,
        chat_service: ChatService,
        file_service: FileEntityService,
    ):
        self._message_repository = message_repository
        self._chat_service = chat_service
        self._file_service = file_service

    async def get_mesage_by_id(
        self,
        session: AsyncSession,
        user: User,
        message_id,
    ):
        message = await session.get(Message, message_id)
        await self._chat_service.get_by_chat_id(
            session, user, message.chat_id
        )  # access checking
        return message

    async def get_messages_by_chat_id(
        self,
        session: AsyncSession,
        user: User,
        chat_id: int,
        page: int,
        size: int,
    ):
        await self._chat_service.get_by_chat_id(session, user, chat_id)
        total_messages_count = await self._message_repository.count_messages(
            session, chat_id
        )
        messages = await self._message_repository.get_messagees(
            session, chat_id, page, size
        )
        return PageSchema(total_items_count=total_messages_count, items=messages)

    async def create(
        self,
        session: AsyncSession,
        user: User,
        create_schema: MessageCreateSchema,
        chat_id: int,
    ):
        chat = await self._chat_service.get_by_chat_id(session, user, chat_id)
        create_schema_dict = create_schema.model_dump(
            exclude=["filenames", "voice_filename"]
        )
        create_schema_dict["sender_id"] = user.id
        create_schema_dict["chat_id"] = chat_id
        create_schema_dict["files_urls"] = []
        for filename in create_schema.filenames:
            file_url = await self._file_service.get_by_filename(session, filename)
            create_schema_dict["files_urls"].append(file_url)
        if create_schema.voice_filename:
            create_schema_dict["voice_url"] = await self._file_service.get_by_filename(
                session, create_schema.voice_filename
            )

        messageSchema = MessageBaseSchema(**create_schema_dict)
        message = Message(**messageSchema.model_dump())
        saved_message = await self._message_repository.save(session, message)
        chat.last_timestamp = saved_message.timestamp
        await session.commit()
        return saved_message

    async def update(
        self,
        session: AsyncSession,
        user: User,
        message_id: int,
        udate_schema: MessageCreateSchema,
    ):
        message = await session.get(Message, message_id)
        if message is None:
            raise EntityNotFoundException("message with given id not found")
        chat_id = message.chat_id
        chat = await self._chat_service.get_by_chat_id(
            session,
            user,
            chat_id,
        )
        if message.sender_id != user.id:
            raise ForbiddenException("only sender can edit message")
        udpate_schema_dict = udate_schema.model_dump(
            exclude=["filenames", "voice_filename"]
        )
        udpate_schema_dict["files_urls"] = []
        for filename in udate_schema.filenames:
            file_url = await self._file_service.get_by_filename(session, filename)
            udpate_schema_dict["files_urls"].append(file_url)
        if udate_schema.voice_filename:
            udpate_schema_dict["voice_url"] = await self._file_service.get_by_filename(
                session, udate_schema.voice_filename
            )
        udpate_schema_dict["timestamp"] = datetime.now(datetime.UTC)

        messageSchema = MessageBaseSchema(**udpate_schema_dict)
        update_model_by_schema(message, messageSchema)
        saved_message = await self._message_repository.save(session, message)
        chat.last_timestamp = saved_message.timestamp
        await session.commit()
        return saved_message
