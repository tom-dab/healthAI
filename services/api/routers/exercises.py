"""
HealthAI Coach — Exercises Router
Endpoints API pour la gestion des exercices
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.security import get_current_user, get_current_admin_user
from ..models.exercise import Exercise, WorkoutLog
from ..schemas.exercise import (
    ExerciseOut, ExerciseCreate, ExerciseUpdate,
    WorkoutLogCreate, WorkoutLogOut
)

router = APIRouter(prefix="/api/v1", tags=["exercises"])


# ─── EXERCISES ───

@router.get("/exercises", response_model=List[ExerciseOut])
async def list_exercises(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    type: str = Query(None, alias="type"),
    muscle_group: str = Query(None),
    difficulty: str = Query(None),
    search: str = Query(None),
    db: Session = Depends(get_db),
):
    """Lister les exercices (paginé, filtrable)"""
    query = db.query(Exercise)

    if type:
        query = query.filter(Exercise.type.ilike(f"%{type}%"))

    if muscle_group:
        query = query.filter(Exercise.muscle_group.ilike(f"%{muscle_group}%"))

    if difficulty:
        query = query.filter(Exercise.difficulty == difficulty)

    if search:
        query = query.filter(Exercise.name.ilike(f"%{search}%"))

    exercises = query.offset(offset).limit(limit).all()
    return [ExerciseOut.from_orm(exercise) for exercise in exercises]


@router.get("/exercises/{exercise_id}", response_model=ExerciseOut)
async def get_exercise(
    exercise_id: str,
    db: Session = Depends(get_db),
):
    """Récupérer détail d'un exercice"""
    try:
        exercise_uuid = uuid.UUID(exercise_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="UUID invalide")

    exercise = db.query(Exercise).filter(Exercise.id == exercise_uuid).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercice non trouvé")
    return ExerciseOut.from_orm(exercise)


@router.post("/exercises", response_model=ExerciseOut, status_code=201)
async def create_exercise(
    data: ExerciseCreate,
    user_id: str = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Créer un nouvel exercice (admin seulement)"""
    # TODO: Vérifier rôle admin
    exercise = Exercise(**data.dict())
    db.add(exercise)
    db.commit()
    db.refresh(exercise)
    return ExerciseOut.from_orm(exercise)


@router.put("/exercises/{exercise_id}", response_model=ExerciseOut)
async def update_exercise(
    exercise_id: str,
    data: ExerciseUpdate,
    user_id: str = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Mettre à jour un exercice (admin seulement)"""
    try:
        exercise_uuid = uuid.UUID(exercise_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="UUID invalide")

    exercise = db.query(Exercise).filter(Exercise.id == exercise_uuid).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercice non trouvé")

    # TODO: Vérifier rôle admin
    for field, value in data.dict(exclude_unset=True).items():
        setattr(exercise, field, value)

    db.commit()
    db.refresh(exercise)
    return ExerciseOut.from_orm(exercise)


@router.delete("/exercises/{exercise_id}", status_code=204)
async def delete_exercise(
    exercise_id: str,
    user_id: str = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Supprimer un exercice (admin seulement)"""
    try:
        exercise_uuid = uuid.UUID(exercise_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="UUID invalide")

    exercise = db.query(Exercise).filter(Exercise.id == exercise_uuid).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercice non trouvé")

    # TODO: Vérifier rôle admin
    db.delete(exercise)
    db.commit()


# ─── WORKOUT LOGS ───

@router.get("/users/{target_user_id}/workout-logs", response_model=List[WorkoutLogOut])
async def get_workout_logs(
    target_user_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    exercise_id: str = Query(None),
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Récupérer les logs d'entraînement d'un utilisateur"""
    try:
        target_uuid = uuid.UUID(target_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="UUID utilisateur invalide")

    # TODO: Vérifier permissions (admin ou propriétaire)
    query = db.query(WorkoutLog).filter(WorkoutLog.user_id == target_uuid)

    if exercise_id:
        try:
            exercise_uuid = uuid.UUID(exercise_id)
            query = query.filter(WorkoutLog.exercise_id == exercise_uuid)
        except ValueError:
            raise HTTPException(status_code=400, detail="UUID exercice invalide")

    logs = query.order_by(WorkoutLog.logged_at.desc()).offset(offset).limit(limit).all()
    return [WorkoutLogOut.from_orm(log) for log in logs]


@router.post("/users/{target_user_id}/workout-logs", response_model=WorkoutLogOut, status_code=201)
async def create_workout_log(
    target_user_id: str,
    data: WorkoutLogCreate,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Logger un entraînement pour un utilisateur"""
    try:
        target_uuid = uuid.UUID(target_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="UUID utilisateur invalide")

    # TODO: Vérifier permissions (admin ou propriétaire)
    # Vérifier que l'exercice existe
    exercise = db.query(Exercise).filter(
        Exercise.id == data.exercise_id
    ).first()
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercice non trouvé")

    log = WorkoutLog(
        user_id=target_uuid,
        **data.dict()
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return WorkoutLogOut.from_orm(log)


@router.delete("/users/{target_user_id}/workout-logs/{log_id}", status_code=204)
async def delete_workout_log(
    target_user_id: str,
    log_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Supprimer un log d'entraînement"""
    try:
        target_uuid = uuid.UUID(target_user_id)
        log_uuid = uuid.UUID(log_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="UUID invalide")

    log = db.query(WorkoutLog).filter(
        WorkoutLog.id == log_uuid,
        WorkoutLog.user_id == target_uuid
    ).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log d'entraînement non trouvé")

    # TODO: Vérifier permissions (admin ou propriétaire)
    db.delete(log)
    db.commit()


# ─── ADMIN: All Workout Logs ───

@router.get("/admin/workout-logs", response_model=List[WorkoutLogOut])
async def get_all_workout_logs(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    user_id: str = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Admin: Récupérer tous les logs d'entraînement (tous utilisateurs)"""
    logs = db.query(WorkoutLog).order_by(WorkoutLog.logged_at.desc()).offset(offset).limit(limit).all()
    return [WorkoutLogOut.from_orm(log) for log in logs]