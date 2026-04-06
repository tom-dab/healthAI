"""
HealthAI Coach — Nutrition Schemas
Schémas Pydantic pour validation et sérialisation des données nutrition
"""
from pydantic import BaseModel, Field
from typing import Optional
import uuid
from datetime import datetime


class NutritionItemBase(BaseModel):
    """Base schema pour nutrition item"""
    name: str = Field(..., min_length=1, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    calories: Optional[float] = Field(None, ge=0, le=9999.99)
    proteins_g: Optional[float] = Field(None, ge=0, le=999.99)
    carbs_g: Optional[float] = Field(None, ge=0, le=999.99)
    fats_g: Optional[float] = Field(None, ge=0, le=999.99)
    fiber_g: Optional[float] = Field(None, ge=0, le=999.99)
    source: Optional[str] = Field(None, max_length=100)


class NutritionItemCreate(NutritionItemBase):
    """Request POST pour créer un nutrition item"""
    pass


class NutritionItemUpdate(BaseModel):
    """Request PUT pour mettre à jour un nutrition item"""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    calories: Optional[float] = Field(None, ge=0, le=9999.99)
    proteins_g: Optional[float] = Field(None, ge=0, le=999.99)
    carbs_g: Optional[float] = Field(None, ge=0, le=999.99)
    fats_g: Optional[float] = Field(None, ge=0, le=999.99)
    fiber_g: Optional[float] = Field(None, ge=0, le=999.99)
    source: Optional[str] = Field(None, max_length=100)


class NutritionItemOut(NutritionItemBase):
    """Réponse GET pour nutrition item"""
    id: uuid.UUID
    created_at: datetime

    class Config:
        from_attributes = True


class FoodLogCreate(BaseModel):
    """Request POST pour logger un aliment"""
    nutrition_item_id: uuid.UUID
    quantity_g: float = Field(..., gt=0, le=9999.99)
    meal_type: str = Field(..., pattern=r'^(breakfast|lunch|dinner|snack)$')


class FoodLogOut(BaseModel):
    """Réponse GET pour food log"""
    id: uuid.UUID
    user_id: uuid.UUID
    nutrition_item_id: uuid.UUID
    quantity_g: float
    meal_type: str
    logged_at: datetime

    class Config:
        from_attributes = True