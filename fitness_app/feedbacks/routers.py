from fastapi import APIRouter, Depends

from fitness_app.auth.dependencies import AuthenticateUser, HasPermission
from fitness_app.auth.permissions import IsCustomer
from fitness_app.core.dependencies import DbSession, FeedbackServiceDep
from fitness_app.core.utils import IdField
from fitness_app.feedbacks.schemas import FeedbackCreateSchema, FeedbackSchema

feedbacks_router = APIRouter(prefix="/customers", tags=["Отзывы"])


@feedbacks_router.post(
    "/{coach_id}",
    summary="Создать отзыв",
    response_model=FeedbackSchema,
    dependencies=[Depends(HasPermission(IsCustomer()))],
)
async def create(
    session: DbSession,
    service: FeedbackServiceDep,
    user: AuthenticateUser,
    schema: FeedbackCreateSchema,
    coach_id: IdField,
):
    feedback = await service.create(session, user, coach_id, schema)
    return FeedbackSchema.model_validate(feedback)


@feedbacks_router.put(
    "/{coach_id}",
    summary="Изменить отзыв",
    response_model=FeedbackSchema,
    dependencies=[Depends(HasPermission(IsCustomer()))],
)
async def update(
    session: DbSession,
    service: FeedbackServiceDep,
    user: AuthenticateUser,
    schema: FeedbackCreateSchema,
    coach_id: IdField,
):
    feedback = await service.update(session, user, coach_id, schema)
    return FeedbackSchema.model_validate(feedback)
