from sqlalchemy.ext.asyncio import AsyncSession

from fitness_app.coaches.models import Coach
from fitness_app.coaches.repositories import CoachRepository
from fitness_app.coaches.services import CoachService
from fitness_app.core.exceptions import EntityNotFoundException, ForbiddenException
from fitness_app.core.utils import update_model_by_schema
from fitness_app.feedbacks.models import Feedback
from fitness_app.feedbacks.repositories import FeedbackRepository
from fitness_app.feedbacks.schemas import FeedbackCreateSchema
from fitness_app.users.models import User
from fitness_app.users.repositories import UserRepository


class FeedbackService:
    def __init__(
        self,
        feedback_repository: FeedbackRepository,
        user_repository: UserRepository,
        coach_repository: CoachRepository,
        coach_service: CoachService,
    ):
        self._feedback_repository = feedback_repository
        self._user_repository = user_repository
        self._coach_repository = coach_repository
        self._coach_service = coach_service

    async def create(
        self,
        session: AsyncSession,
        user: User,
        coach_id: int,
        schema: FeedbackCreateSchema,
    ):
        customer = user.customer_info
        coach = await self._coach_service.get_by_id(session, coach_id)
        if not await self._user_repository.is_exists_assignment(
            session, customer.id, coach_id
        ):
            raise ForbiddenException("Customer is not assigned to the coach")
        if await self._feedback_repository.is_exists(session, coach_id, customer.id):
            raise EntityNotFoundException(
                "Feedback with given coach id and customer id already exists"
            )
        feedback = Feedback(**schema.model_dump())
        setattr(feedback, "coach_id", coach_id)
        setattr(feedback, "customer_id", customer.id)
        setattr(feedback, "cusromer", customer)
        setattr(feedback, "coach", coach)
        feedback = await self._feedback_repository.save(session, feedback)
        await self._coach_repository.add_feedback(session, coach_id, feedback)

        return feedback

    async def update(
        self,
        session: AsyncSession,
        user: User,
        coach_id: int,
        schema: FeedbackCreateSchema,
    ):

        customer = user.customer_info
        coach = await session.get(Coach, coach_id)
        if not await self._feedback_repository.is_exists(
            session, coach_id, customer.id
        ):
            raise EntityNotFoundException(
                "Not found feedback with given coach id and customer id"
            )
        feedback = await self._feedback_repository.get_by_ids(
            session, coach_id, customer.id
        )
        update_model_by_schema(feedback, schema)
        await self._feedback_repository.save(session, feedback)
        await self._coach_repository.save(session, coach)
        return feedback
