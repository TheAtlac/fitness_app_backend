from fastapi import APIRouter, Depends

from fitness_app.auth.dependencies import AuthenticateUser, HasPermission
from fitness_app.auth.permissions import Authenticated
from fitness_app.core.dependencies import DbSession, MessageServiceDep
from fitness_app.core.schemas import PageSchema
from fitness_app.core.utils import IdField, PageField, SizeField
from fitness_app.messages.schemas import MessageCreateSchema, MessageSchema

messages_router = APIRouter(prefix="/messages", tags=["Сообщения"])


@messages_router.get(
    "/{chat_id}",
    summary="Получить список всех сообщений из чата",
    response_model=PageSchema,
    dependencies=[Depends(HasPermission(Authenticated()))],
)
async def get_all(
    session: DbSession,
    service: MessageServiceDep,
    chat_id: IdField,
    user: AuthenticateUser,
    page: PageField = 0,
    size: SizeField = 10,
):
    messages = await service.get_messages_by_chat_id(session, user, chat_id, page, size)
    return PageSchema(
        total_items_count=messages.total_items_count,
        items=list(map(MessageSchema.model_validate, messages.items)),
    )


@messages_router.post(
    "/{chat_id}",
    summary="Отправить сообщение в чат",
    response_model=MessageSchema,
    dependencies=[Depends(HasPermission(Authenticated()))],
)
async def send(
    session: DbSession,
    service: MessageServiceDep,
    chat_id: IdField,
    user: AuthenticateUser,
    schema: MessageCreateSchema,
):
    message = await service.create(session, user, schema, chat_id)
    return MessageSchema.model_validate(message)
