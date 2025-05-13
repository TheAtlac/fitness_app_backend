import logging
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from fitness_app.core.db_manager import DatabaseManager  # isort: split

from fitness_app.auth.routers import auth_router
from fitness_app.auth.services import AuthService, PasswordService, TokenService
from fitness_app.chats.repositories import ChatRepository
from fitness_app.chats.routers import chats_router
from fitness_app.chats.services import ChatService
from fitness_app.coaches.repositories import CoachRepository
from fitness_app.coaches.routers import coaches_router
from fitness_app.coaches.services import CoachService
from fitness_app.core.exceptions import (
    AppException,
    handle_app_exception,
    handle_validation_exception,
)
from fitness_app.core.settings import AppSettings
from fitness_app.customers.repositories import CustomerRepository
from fitness_app.customers.routers import customers_router
from fitness_app.customers.services import CustomerService
from fitness_app.diaries.repositories import DiaryRepository
from fitness_app.diaries.routers import diaries_router
from fitness_app.diaries.services import DiaryService
from fitness_app.exercises.repositories import ExerciseRepository
from fitness_app.exercises.routers import exercises_router
from fitness_app.exercises.services import ExerciseService
from fitness_app.feedbacks.repositories import FeedbackRepository
from fitness_app.feedbacks.routers import feedbacks_router
from fitness_app.feedbacks.services import FeedbackService
from fitness_app.file_entities.repositories import FileEntityRepository
from fitness_app.file_entities.routers import file_entities_router
from fitness_app.file_entities.services import FileEntityService
from fitness_app.messages.repositories import MessageRepository
from fitness_app.messages.routers import messages_router
from fitness_app.messages.services import MessageService
from fitness_app.steps.repositories import StepsRepository
from fitness_app.steps.routers import steps_router
from fitness_app.steps.services import StepsService
from fitness_app.store.repositories import StoreRepository
from fitness_app.store.routers import store_router
from fitness_app.store.services import StoreService
from fitness_app.users.repositories import UserRepository
from fitness_app.users.routers import users_router
from fitness_app.users.services import UserService
from fitness_app.water_entries.repositories import WaterEntryRepository
from fitness_app.water_entries.routers import water_entries_router
from fitness_app.water_entries.services import WaterEntryService
from fitness_app.workouts.ExerciseWorkoutService import ExerciseWorkoutService
from fitness_app.workouts.repositories import (
    ExerciseWorkoutRepository,
    WorkoutRepository,
)
from fitness_app.workouts.routers import workouts_router
from fitness_app.workouts.WorkoutService import WorkoutService


def create_app(settings: AppSettings | None = None) -> FastAPI:
    if settings is None:
        settings = AppSettings()

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    app = FastAPI(
        title="Приложение-ассистент для формирования плана фитнес-тренировок",
        lifespan=_app_lifespan,
        servers=[
            {"url": "http://localhost:8080", "description": "Локальный сервер"},
            {"url": "http://176.109.107.222:8080", "description": "Dev сервер"},
        ],
        responses={
            400: {"description": "Неверный формат входных данных"},
        },
    )

    """ Setup global dependencies """
    _setup_app_dependencies(app, settings)

    """ Setup middlewares """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    """ Setup routers """
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(water_entries_router)
    app.include_router(workouts_router)
    app.include_router(exercises_router)
    app.include_router(file_entities_router)
    app.include_router(customers_router)
    app.include_router(coaches_router)
    app.include_router(chats_router)
    app.include_router(messages_router)
    app.include_router(exercises_router)
    app.include_router(workouts_router)
    app.include_router(steps_router)
    app.include_router(diaries_router)
    app.include_router(feedbacks_router)
    app.include_router(store_router)

    """ Setup exception handlers """
    app.add_exception_handler(AppException, handle_app_exception)
    app.add_exception_handler(RequestValidationError, handle_validation_exception)

    return app


def _setup_app_dependencies(app: FastAPI, settings: AppSettings):
    app.state.settings = settings
    app.state.database_manager = DatabaseManager(settings.db_url)

    workout_repository = WorkoutRepository()
    exercise_workout_repository = ExerciseWorkoutRepository()
    user_repository = UserRepository()
    water_entry_repository = WaterEntryRepository()
    file_entity_repository = FileEntityRepository()
    exercise_repository = ExerciseRepository()
    coach_repository = CoachRepository()
    customer_repository = CustomerRepository()
    message_repository = MessageRepository()
    chat_repository = ChatRepository()
    steps_repository = StepsRepository()
    diary_repository = DiaryRepository()
    feedback_repository = FeedbackRepository()
    store_repository = StoreRepository()

    password_service = PasswordService()
    password_service = PasswordService()
    token_service = TokenService(
        settings.auth_token_secret_key, settings.auth_token_lifetime
    )
    auth_service = AuthService(password_service, token_service, user_repository)
    user_service = UserService(password_service, user_repository)
    water_entry_service = WaterEntryService(
        water_entry_repository, settings.goal_water_volume
    )
    file_entity_service = FileEntityService(
        settings.region,
        settings.aws_access_key_id,
        settings.aws_secret_access_key,
        settings.bucket_name,
        settings.aws_endpoint,
        settings.aws_access_domain_name,
        file_entity_repository,
        exercise_repository,
    )
    chat_service = ChatService(chat_repository, user_service)
    coach_service = CoachService(
        coach_repository, user_repository, user_service, chat_service
    )
    customer_service = CustomerService(
        customer_repository, user_repository, user_service, chat_service
    )
    exercise_service = ExerciseService(exercise_repository, file_entity_service)
    workout_service = WorkoutService(
        workout_repository,
        exercise_workout_repository,
        exercise_service,
        chat_service,
        coach_service,
        customer_service,
        user_service,
    )
    exercise_workout_service = ExerciseWorkoutService(
        workout_service, exercise_workout_repository, exercise_service
    )
    message_service = MessageService(
        message_repository, chat_service, file_entity_service
    )
    steps_service = StepsService(steps_repository, settings.default_steps_goal)
    diary_service = DiaryService(diary_repository, file_entity_service)
    feedback_service = FeedbackService(
        feedback_repository, user_repository, coach_repository, coach_service
    )
    store_service = StoreService(store_repository)

    app.state.workout_service = workout_service
    app.state.exercise_workout_service = exercise_workout_service
    app.state.auth_service = auth_service
    app.state.user_service = user_service
    app.state.water_entry_service = water_entry_service
    app.state.file_entity_service = file_entity_service
    app.state.exercise_service = exercise_service
    app.state.coach_service = coach_service
    app.state.customer_service = customer_service
    app.state.chat_service = chat_service
    app.state.message_service = message_service
    app.state.steps_service = steps_service
    app.state.diary_service = diary_service
    app.state.feedback_service = feedback_service
    app.state.store_service = store_service


@asynccontextmanager
async def _app_lifespan(app: FastAPI):
    # settings: AppSettings = app.state.settings
    db: DatabaseManager = app.state.database_manager

    await db.initialize()

    # if settings.initial_user is not None:
    #     user_service: UserService = app.state.user_service
    #     async with db.create_session() as session:
    #         try:
    #             await user_service.create(session, settings.initial_user)
    #             logging.info("Initial user was successfully created")
    #         except EntityAlreadyExistsException:
    #             logging.info("Initial user already exists. Skipped")

    yield
    await db.dispose()
