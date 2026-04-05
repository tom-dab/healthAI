"""
HealthAI Coach — User Model
Modèle SQLAlchemy pour la table users
"""
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Integer, Numeric, DateTime, CheckConstraint, Index
from sqlalchemy.dialects.postgresql import UUID

from core.database import Base  # ← était : from ..core.database import Base


class User(Base):
    """
    Modèle utilisateur HealthAI Coach.
    Représente la table 'users' en base de données.
    """
    __tablename__ = "users"

    # Identifiant
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

    # Authentification
    email         = Column(String(255), unique=True, nullable=False, index=True)
    username      = Column(String(100), nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # Données démographiques
    age       = Column(Integer,      nullable=True)
    gender    = Column(String(10),   nullable=True)
    height_cm = Column(Numeric(5,2), nullable=True)
    weight_kg = Column(Numeric(5,2), nullable=True)

    # Activité de base
    water_intake_liters = Column(Numeric(4,2), nullable=True)
    workout_frequency   = Column(Integer,      nullable=True)

    # Objectif & niveau
    goal          = Column(String(50), default="general_health", nullable=False)
    fitness_level = Column(String(20), default="beginner",       nullable=True)

    # Abonnement & rôle
    plan = Column(String(20), default="free",  nullable=False)
    role = Column(String(20), default="user",  nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_user_email",      "email"),
        Index("idx_user_username",   "username"),
        Index("idx_user_created_at", "created_at"),
        CheckConstraint("age > 0 AND age < 120", name="check_user_age"),
        CheckConstraint("height_cm > 0",         name="check_user_height"),
        CheckConstraint("weight_kg > 0",          name="check_user_weight"),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
