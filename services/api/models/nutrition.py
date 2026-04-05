"""
HealthAI Coach — Nutrition Model
Modèle SQLAlchemy pour nutrition_items et food_logs
"""
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID

from core.database import Base


class NutritionItem(Base):
    """
    Modèle pour la table nutrition_items.
    Représente des aliments avec leurs valeurs nutritionnelles.
    """
    __tablename__ = "nutrition_items"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=True)
    
    # Valeurs nutritionnelles (pour 100g)
    calories = Column(Numeric(7, 2), nullable=True)
    proteins_g = Column(Numeric(7, 2), nullable=True)
    carbs_g = Column(Numeric(7, 2), nullable=True)
    fats_g = Column(Numeric(7, 2), nullable=True)
    fiber_g = Column(Numeric(7, 2), nullable=True)
    
    # Source des données
    source = Column(String(100), nullable=True)  # ex: "Kaggle", "USDA"
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_nutrition_name', 'name'),
        Index('idx_nutrition_category', 'category'),
    )


class FoodLog(Base):
    """
    Modèle pour la table food_logs.
    Représente les aliments loggés par les utilisateurs.
    """
    __tablename__ = "food_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    nutrition_item_id = Column(UUID(as_uuid=True), ForeignKey("nutrition_items.id"), nullable=False)
    
    quantity_g = Column(Numeric(7, 2), nullable=False)  # Quantité en grammes
    meal_type = Column(String(20), nullable=False)  # breakfast, lunch, dinner, snack
    logged_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_food_log_user', 'user_id'),
        Index('idx_food_log_date', 'logged_at'),
    )
