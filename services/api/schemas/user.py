"""
HealthAI Coach — User Schemas
Pydantic schemas pour validation et sérialisation des users
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


# ─────────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────────
class GenderEnum(str, Enum):
    """Genre utilisateur."""
    male = "male"
    female = "female"
    other = "other"


class GoalEnum(str, Enum):
    """Objectif personnel utilisateur."""
    weight_loss = "weight_loss"
    muscle_gain = "muscle_gain"
    sleep_improvement = "sleep_improvement"
    maintenance = "maintenance"
    general_health = "general_health"


class PlanEnum(str, Enum):
    """Plan d'abonnement."""
    free = "free"
    premium = "premium"
    premium_plus = "premium_plus"


# ─────────────────────────────────────────────────────────────────
# Base Schema (champs communs)
# ─────────────────────────────────────────────────────────────────
class UserBase(BaseModel):
    """Champs de base partagés par tous les user schemas."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    age: Optional[int] = Field(None, ge=1, le=120)
    gender: Optional[GenderEnum] = None
    height_cm: Optional[float] = Field(None, gt=0)
    weight_kg: Optional[float] = Field(None, gt=0)
    goal: GoalEnum = GoalEnum.general_health
    plan: PlanEnum = PlanEnum.free


# ─────────────────────────────────────────────────────────────────
# Request Schemas (Input)
# ─────────────────────────────────────────────────────────────────
class UserCreate(UserBase):
    """Schema pour créer un nouvel utilisateur (POST)."""
    password: str = Field(..., min_length=8, description="Minimum 8 caractères")


class UserUpdate(BaseModel):
    """Schema pour mettre à jour un utilisateur (PUT)."""
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    age: Optional[int] = Field(None, ge=1, le=120)
    gender: Optional[GenderEnum] = None
    height_cm: Optional[float] = Field(None, gt=0)
    weight_kg: Optional[float] = Field(None, gt=0)
    goal: Optional[GoalEnum] = None
    plan: Optional[PlanEnum] = None


class LoginRequest(BaseModel):
    """Schema pour login."""
    email: EmailStr
    password: str


# ─────────────────────────────────────────────────────────────────
# Response Schemas (Output)
# ─────────────────────────────────────────────────────────────────
class UserOut(UserBase):
    """Schema de réponse pour un utilisateur (GET/POST/PUT)."""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True  # Permet de mapper depuis ORM


class UserListResponse(BaseModel):
    """Schema pour une liste paginée d'utilisateurs."""
    total: int = Field(..., ge=0)
    limit: int = Field(..., ge=1)
    offset: int = Field(..., ge=0)
    items: list[UserOut]


# ─────────────────────────────────────────────────────────────────
# Auth Responses
# ─────────────────────────────────────────────────────────────────
class TokenResponse(BaseModel):
    """Schema pour réponse d'authentification."""
    access_token: str = Field(..., description="JWT token")
    token_type: str = Field(default="bearer")
    user: UserOut = Field(..., description="Données utilisateur")


class ProfileResponse(BaseModel):
    """Schema pour réponse GET /auth/profile."""
    user: UserOut


# ─────────────────────────────────────────────────────────────────
# Messages d'erreur standardisés
# ─────────────────────────────────────────────────────────────────
class ErrorResponse(BaseModel):
    """Schema pour erreur API."""
    detail: str
    status_code: int = Field(..., ge=400)
