"""
HealthAI Coach — Exercise Model
Modèles SQLAlchemy pour exercises et workout_logs
"""
from datetime import datetime
import uuid
from sqlalchemy import Column, String, Text, Integer, Numeric, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID

from core.database import Base  # ← était : from ..core.database import Base


class Exercise(Base):
    """
    Modèle pour la table exercises.
    Source : ExerciseDB API / GitHub Repository
    """
    __tablename__ = "exercises"

    id           = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    name         = Column(String(255), nullable=False, unique=True, index=True)
    type         = Column(String(50),  nullable=True)
    muscle_group = Column(String(100), nullable=True)
    equipment    = Column(String(100), nullable=True)
    difficulty   = Column(String(20),  nullable=False, default="intermediate")
    instructions = Column(Text,        nullable=True)

    external_id  = Column(String(100), nullable=True)
    source       = Column(String(100), nullable=True)
    created_at   = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_exercise_name",       "name"),
        Index("idx_exercise_type",       "type"),
        Index("idx_exercise_difficulty", "difficulty"),
    )


class WorkoutLog(Base):
    """
    Modèle pour la table workout_logs.
    Journal d'entraînement des utilisateurs.
    """
    __tablename__ = "workout_logs"

    id          = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)
    user_id     = Column(UUID(as_uuid=True), ForeignKey("users.id"),     nullable=False, index=True)
    exercise_id = Column(UUID(as_uuid=True), ForeignKey("exercises.id"), nullable=False)

    duration_min    = Column(Integer,      nullable=True)
    sets            = Column(Integer,      nullable=True)
    reps            = Column(Integer,      nullable=True)
    calories_burned = Column(Numeric(7,2), nullable=True)  # ajout Hanane
    logged_at       = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index("idx_workout_log_user", "user_id"),
        Index("idx_workout_log_date", "logged_at"),
    )
