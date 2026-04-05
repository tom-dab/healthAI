"""
HealthAI Coach — Metrics Router
Endpoints pour les métriques et statistiques (admin)
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Any

from core.database import get_db
from core.security import get_current_admin_user
from models.user import User
from models.nutrition import NutritionItem, FoodLog
from models.exercise import Exercise, WorkoutLog

router = APIRouter(prefix="/api/v1", tags=["metrics"])


@router.get("/metrics", response_model=Dict[str, Any])
async def get_global_metrics(
    user_id: str = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Métriques globales de l'application (admin seulement).
    
    Retourne des statistiques sur:
    - Utilisateurs (total, par plan, par genre)
    - Aliments et exercices (catalogue)
    - Logs (activité globale)
    - Métriques de santé (moyennes)
    """
    # Comptes utilisateurs
    total_users = db.query(func.count(User.id)).scalar()
    users_by_plan = db.query(User.plan, func.count(User.id)).group_by(User.plan).all()
    users_by_gender = db.query(User.gender, func.count(User.id)).group_by(User.gender).all()
    
    # Moyennes des métriques utilisateurs
    avg_weight = db.query(func.avg(User.weight_kg)).filter(User.weight_kg.isnot(None)).scalar()
    avg_height = db.query(func.avg(User.height_cm)).filter(User.height_cm.isnot(None)).scalar()
    avg_age = db.query(func.avg(User.age)).filter(User.age.isnot(None)).scalar()
    
    # Catalogue
    total_nutrition_items = db.query(func.count(NutritionItem.id)).scalar()
    total_exercises = db.query(func.count(Exercise.id)).scalar()
    
    # Logs d'activité
    total_food_logs = db.query(func.count(FoodLog.id)).scalar()
    total_workout_logs = db.query(func.count(WorkoutLog.id)).scalar()
    
    # Logs récents (dernière semaine)
    from datetime import datetime, timedelta
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_food_logs = db.query(func.count(FoodLog.id)).filter(FoodLog.logged_at >= week_ago).scalar()
    recent_workout_logs = db.query(func.count(WorkoutLog.id)).filter(WorkoutLog.logged_at >= week_ago).scalar()
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "users": {
            "total": total_users,
            "by_plan": dict(users_by_plan),
            "by_gender": dict(users_by_gender),
            "avg_weight_kg": round(avg_weight, 1) if avg_weight else None,
            "avg_height_cm": round(avg_height, 1) if avg_height else None,
            "avg_age": round(avg_age, 1) if avg_age else None,
        },
        "catalog": {
            "nutrition_items": total_nutrition_items,
            "exercises": total_exercises,
        },
        "activity": {
            "total_food_logs": total_food_logs,
            "total_workout_logs": total_workout_logs,
            "recent_food_logs_7d": recent_food_logs,
            "recent_workout_logs_7d": recent_workout_logs,
        }
    }


@router.get("/metrics/users/{user_id}", response_model=Dict[str, Any])
async def get_user_metrics(
    target_user_id: str,
    user_id: str = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Métriques détaillées d'un utilisateur spécifique (admin seulement).
    
    Inclut: logs nutrition, logs workout, statistiques personnelles.
    """
    from uuid import UUID
    try:
        target_uuid = UUID(target_user_id)
    except ValueError:
        return {"error": "UUID invalide"}
    
    # Infos utilisateur
    user = db.query(User).filter(User.id == target_uuid).first()
    if not user:
        return {"error": "Utilisateur non trouvé"}
    
    # Comptes logs
    food_logs_count = db.query(func.count(FoodLog.id)).filter(FoodLog.user_id == target_uuid).scalar()
    workout_logs_count = db.query(func.count(WorkoutLog.id)).filter(WorkoutLog.user_id == target_uuid).scalar()
    
    # Logs récents
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_food = db.query(func.count(FoodLog.id)).filter(
        FoodLog.user_id == target_uuid,
        FoodLog.logged_at >= week_ago
    ).scalar()
    recent_workout = db.query(func.count(WorkoutLog.id)).filter(
        WorkoutLog.user_id == target_uuid,
        WorkoutLog.logged_at >= week_ago
    ).scalar()
    
    return {
        "user_id": str(user.id),
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "plan": user.plan,
        "goal": user.goal,
        "profile": {
            "age": user.age,
            "gender": user.gender,
            "height_cm": user.height_cm,
            "weight_kg": user.weight_kg,
        },
        "activity": {
            "total_food_logs": food_logs_count,
            "total_workout_logs": workout_logs_count,
            "recent_food_logs_7d": recent_food,
            "recent_workout_logs_7d": recent_workout,
        },
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }