"""
HealthAI Coach — Nutrition Model
Modèles SQLAlchemy pour nutrition_items et food_logs
"""
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID

from core.database import Base  # ← était : from ..core.database import Base


class NutritionItem(Base):
    """
    Modèle pour la table nutrition_items.
    Source : Daily Food & Nutrition Dataset (Kaggle)
    """
    __tablename__ = "nutrition_items"

    id       = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name     = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=True)
    meal_type = Column(String(50), nullable=True)

    # Macronutriments (pour 100g)
    calories   = Column(Numeric(7,2), default=0)
    proteins_g = Column(Numeric(7,2), default=0)
    carbs_g    = Column(Numeric(7,2), default=0)
    fats_g     = Column(Numeric(7,2), default=0)
    fiber_g    = Column(Numeric(7,2), default=0)

    # Micronutriments (enrichissement Hanane)
    sugar_g        = Column(Numeric(7,2), default=0)
    sodium_mg      = Column(Numeric(7,2), default=0)
    cholesterol_mg = Column(Numeric(7,2), default=0)
    water_ml       = Column(Numeric(7,2), default=0)

    source     = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_nutrition_name",     "name"),
        Index("idx_nutrition_category", "category"),
    )


class FoodLog(Base):
    """
    Modèle pour la table food_logs.
    Journal alimentaire quotidien des utilisateurs.
    """
    __tablename__ = "food_logs"

    id                = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id           = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    nutrition_item_id = Column(UUID(as_uuid=True), ForeignKey("nutrition_items.id"), nullable=False)

    quantity_g = Column(Numeric(7,2), nullable=False)
    meal_type  = Column(String(20),   nullable=True)
    logged_at  = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_food_log_user", "user_id"),
        Index("idx_food_log_date", "logged_at"),
    )
