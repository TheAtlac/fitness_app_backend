from datetime import datetime
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, ConfigDict

from fitness_app.chats.schemas import ChatSchema
from fitness_app.coaches.schemas import CoachSchema
from fitness_app.customers.schemas import CustomerSchema
from fitness_app.exercises.schemas import ExerciseSchema


class TypeConnection(StrEnum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"


class Stages(StrEnum):
    WARM_UP = "WARM_UP"
    MAIN = "MAIN"
    COOL_DOWN = "COOL_DOWN"


class ExerciseWorkoutSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    exercise_id: int
    workout_id: int
    num_order: int
    num_sets: Optional[int] = None
    num_sets_done: int
    num_reps: Optional[int] = None
    stage: Stages

    exercise: Optional["ExerciseSchema"] = None


class ExerciseWorkoutCreateSchema(BaseModel):
    exercise_id: int
    workout_id: int
    num_order: int
    num_sets: Optional[int] = None
    num_sets_done: Optional[int] = None
    num_reps: Optional[int] = None
    stage: Stages


class ExerciseWorkoutUpdateSchema(BaseModel):
    id: int
    exercise_id: int
    num_order: int
    num_sets: Optional[int] = None
    num_sets_done: Optional[int] = None
    num_reps: Optional[int] = None
    stage: Stages


class WorkoutCreateExerciseWorkoutSchema(BaseModel):
    exercise_id: int
    num_order: int
    num_sets: Optional[int] = None
    num_sets_done: Optional[int] = None
    num_reps: Optional[int] = None
    stage: Stages


class WorkoutSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    coach_id: Optional[int] = None
    customer_id: Optional[int] = None
    chat_id: Optional[int] = None
    name: str
    type_connection: Optional[TypeConnection] = None
    time_start: Optional[datetime] = None

    exercise_workouts: Optional[list["ExerciseWorkoutSchema"]] = []
    customer: Optional["CustomerSchema"] = None
    coach: Optional["CoachSchema"] = None
    chat: Optional["ChatSchema"] = None


class WorkoutCreateSchema(BaseModel):
    coach_id: Optional[int] = None
    customer_id: Optional[int] = None
    name: str
    type_connection: Optional[TypeConnection] = None
    time_start: Optional[datetime] = None

    exercise_workouts_create: Optional[list[WorkoutCreateExerciseWorkoutSchema]] = []


class WorkoutUpdateSchema(BaseModel):
    id: int
    name: str
    type_connection: Optional[TypeConnection] = None
    time_start: Optional[datetime] = None


class WorkoutFindSchema(BaseModel):
    name: Optional[str] = None
    type_connection: Optional[TypeConnection] = None
    from_time_start: Optional[datetime] = None
    to_time_start: Optional[datetime] = None
