"""
HealthAI Coach — Exercise Schemas
Schémas Pydantic pour validation et sérialisation des données exercise
"""
from pydantic import BaseModel, Field
from typing import Optional
import uuid
from datetime import datetime


class ExerciseBase(BaseModel):
    """Base schema pour exercise"""
    name: str = Field(..., min_length=1, max_length=255)
    type: Optional[str] = Field(None, max_length=50)
    muscle_group: Optional[str] = Field(None, max_length=100)
    equipment: Optional[str] = Field(None, max_length=100)
    difficulty: str = Field(..., regex=r'^(beginner|intermediate|advanced)$')
    instructions: Optional[str] = None
    external_id: Optional[str] = Field(None, max_length=100)
    source: Optional[str] = Field(None, max_length=100)


class ExerciseCreate(ExerciseBase):
    """Request POST pour créer un exercise"""
    pass


class ExerciseUpdate(BaseModel):
    """Request PUT pour mettre à jour un exercise"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[str] = Field(None, max_length=50)
    muscle_group: Optional[str] = Field(None, max_length=100)
    equipment: Optional[str] = Field(None, max_length=100)
    difficulty: Optional[str] = Field(None, regex=r'^(beginner|intermediate|advanced)$')
    instructions: Optional[str] = None
    external_id: Optional[str] = Field(None, max_length=100)
    source: Optional[str] = Field(None, max_length=100)


class ExerciseOut(ExerciseBase):
    """Réponse GET pour exercise"""
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class WorkoutLogCreate(BaseModel):
    """Request POST pour logger un workout"""
    exercise_id: uuid.UUID
    duration_min: int = Field(..., gt=0, le=1440)  # Max 24h
    sets: Optional[int] = Field(None, ge=1, le=100)
    reps: Optional[int] = Field(None, ge=1, le=1000)


class WorkoutLogOut(BaseModel):
    """Réponse GET pour workout log"""
    id: uuid.UUID
    user_id: uuid.UUID
    exercise_id: uuid.UUID
    duration_min: int
    sets: Optional[int]
    reps: Optional[int]
    logged_at: datetime

    class Config:
        from_attributes = True