from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from fitness_app.auth.services import AuthService
from fitness_app.chats.services import ChatService
from fitness_app.coaches.services import CoachService
from fitness_app.core.db_manager import DatabaseManager
from fitness_app.customers.services import CustomerService
from fitness_app.diaries.services import DiaryService
from fitness_app.exercises.services import ExerciseService
from fitness_app.feedbacks.services import FeedbackService
from fitness_app.file_entities.services import FileEntityService
from fitness_app.messages.services import MessageService
from fitness_app.steps.services import StepsService
from fitness_app.store.services import StoreService
from fitness_app.users.services import UserService
from fitness_app.water_entries.services import WaterEntryService
from fitness_app.workouts.ExerciseWorkoutService import ExerciseWorkoutService
from fitness_app.workouts.WorkoutService import WorkoutService


def db_manager(request: Request) -> DatabaseManager:
    return request.app.state.database_manager


async def db_session(db_manager: Annotated[DatabaseManager, Depends(db_manager)]):
    async with db_manager.create_session() as session:
        yield session


def auth_service(request: Request) -> AuthService:
    return request.app.state.auth_service


def user_service(request: Request) -> UserService:
    return request.app.state.user_service


def water_entry_service(request: Request) -> WaterEntryService:
    return request.app.state.water_entry_service


def workout_service(request: Request) -> WorkoutService:
    return request.app.state.workout_service


def exercise_workout_service(request: Request) -> ExerciseWorkoutService:
    return request.app.state.exercise_workout_service


def file_entity_service(request: Request) -> FileEntityService:
    return request.app.state.file_entity_service


def exercise_service(request: Request) -> ExerciseService:
    return request.app.state.exercise_service


def coach_service(request: Request) -> CoachService:
    return request.app.state.coach_service


def customer_service(request: Request) -> CustomerService:
    return request.app.state.customer_service


def message_service(request: Request) -> MessageService:
    return request.app.state.message_service


def chat_service(request: Request) -> ChatService:
    return request.app.state.chat_service


def steps_service(request: Request) -> StepsService:
    return request.app.state.steps_service


def diary_service(request: Request) -> DiaryService:
    return request.app.state.diary_service


def feedback_service(request: Request) -> FeedbackService:
    return request.app.state.feedback_service


def store_service(request: Request) -> StoreService:
    return request.app.state.store_service


DbSession = Annotated[AsyncSession, Depends(db_session)]
AuthServiceDep = Annotated[AuthService, Depends(auth_service)]
UserServiceDep = Annotated[UserService, Depends(user_service)]
WaterEntryServiceDep = Annotated[WaterEntryService, Depends(water_entry_service)]
WorkoutServiceDep = Annotated[WorkoutService, Depends(workout_service)]
ExerciseWorkoutServiceDep = Annotated[
    ExerciseWorkoutService, Depends(exercise_workout_service)
]
FileEntityServiceDep = Annotated[FileEntityService, Depends(file_entity_service)]
ExerciseServiceDep = Annotated[ExerciseService, Depends(exercise_service)]
CoachServiceDep = Annotated[CoachService, Depends(coach_service)]
StepsServiceDep = Annotated[StepsService, Depends(steps_service)]
CustomerServiceDep = Annotated[CustomerService, Depends(customer_service)]
MessageServiceDep = Annotated[MessageService, Depends(message_service)]
ChatServiceDep = Annotated[ChatService, Depends(chat_service)]
DiaryServiceDep = Annotated[DiaryService, Depends(diary_service)]
FeedbackServiceDep = Annotated[FeedbackService, Depends(feedback_service)]
StoreServiceDep = Annotated[StoreService, Depends(store_service)]
