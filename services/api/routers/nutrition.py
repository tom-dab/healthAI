"""
HealthAI Coach — Nutrition Router
Endpoints API pour la gestion de la nutrition
"""
import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from ..core.database import get_db
from ..core.security import get_current_user, get_current_admin_user
from ..models.nutrition import NutritionItem, FoodLog
from ..schemas.nutrition import (
    NutritionItemOut, NutritionItemCreate, NutritionItemUpdate,
    FoodLogCreate, FoodLogOut
)

router = APIRouter(prefix="/api/v1", tags=["nutrition"])


# ─── NUTRITION ITEMS ───

@router.get("/nutrition", response_model=List[NutritionItemOut])
async def list_nutrition_items(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category: str = Query(None),
    search: str = Query(None),
    db: Session = Depends(get_db),
):
    """Lister les aliments (paginé, filtrable)"""
    query = db.query(NutritionItem)

    if category:
        query = query.filter(NutritionItem.category.ilike(f"%{category}%"))

    if search:
        query = query.filter(NutritionItem.name.ilike(f"%{search}%"))

    items = query.offset(offset).limit(limit).all()
    return [NutritionItemOut.from_orm(item) for item in items]


@router.get("/nutrition/{item_id}", response_model=NutritionItemOut)
async def get_nutrition_item(
    item_id: str,
    db: Session = Depends(get_db),
):
    """Récupérer détail d'un aliment"""
    try:
        item_uuid = uuid.UUID(item_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="UUID invalide")

    item = db.query(NutritionItem).filter(NutritionItem.id == item_uuid).first()
    if not item:
        raise HTTPException(status_code=404, detail="Aliment non trouvé")
    return NutritionItemOut.from_orm(item)


@router.post("/nutrition", response_model=NutritionItemOut, status_code=201)
async def create_nutrition_item(
    data: NutritionItemCreate,
    user_id: str = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Créer un nouvel aliment (admin seulement)"""
    # TODO: Vérifier rôle admin
    item = NutritionItem(**data.dict())
    db.add(item)
    db.commit()
    db.refresh(item)
    return NutritionItemOut.from_orm(item)


@router.put("/nutrition/{item_id}", response_model=NutritionItemOut)
async def update_nutrition_item(
    item_id: str,
    data: NutritionItemUpdate,
    user_id: str = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Mettre à jour un aliment (admin seulement)"""
    try:
        item_uuid = uuid.UUID(item_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="UUID invalide")

    item = db.query(NutritionItem).filter(NutritionItem.id == item_uuid).first()
    if not item:
        raise HTTPException(status_code=404, detail="Aliment non trouvé")

    # TODO: Vérifier rôle admin
    for field, value in data.dict(exclude_unset=True).items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return NutritionItemOut.from_orm(item)


@router.delete("/nutrition/{item_id}", status_code=204)
async def delete_nutrition_item(
    item_id: str,
    user_id: str = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Supprimer un aliment (admin seulement)"""
    try:
        item_uuid = uuid.UUID(item_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="UUID invalide")

    item = db.query(NutritionItem).filter(NutritionItem.id == item_uuid).first()
    if not item:
        raise HTTPException(status_code=404, detail="Aliment non trouvé")

    # TODO: Vérifier rôle admin
    db.delete(item)
    db.commit()


# ─── FOOD LOGS ───

@router.get("/users/{target_user_id}/food-logs", response_model=List[FoodLogOut])
async def get_food_logs(
    target_user_id: str,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    meal_type: str = Query(None),
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Récupérer les logs alimentaires d'un utilisateur"""
    try:
        target_uuid = uuid.UUID(target_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="UUID utilisateur invalide")

    # TODO: Vérifier permissions (admin ou propriétaire)
    query = db.query(FoodLog).filter(FoodLog.user_id == target_uuid)

    if meal_type:
        query = query.filter(FoodLog.meal_type == meal_type)

    logs = query.order_by(FoodLog.logged_at.desc()).offset(offset).limit(limit).all()
    return [FoodLogOut.from_orm(log) for log in logs]


@router.post("/users/{target_user_id}/food-logs", response_model=FoodLogOut, status_code=201)
async def create_food_log(
    target_user_id: str,
    data: FoodLogCreate,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Logger un aliment pour un utilisateur"""
    try:
        target_uuid = uuid.UUID(target_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="UUID utilisateur invalide")

    # TODO: Vérifier permissions (admin ou propriétaire)
    # Vérifier que l'aliment existe
    nutrition_item = db.query(NutritionItem).filter(
        NutritionItem.id == data.nutrition_item_id
    ).first()
    if not nutrition_item:
        raise HTTPException(status_code=404, detail="Aliment non trouvé")

    log = FoodLog(
        user_id=target_uuid,
        **data.dict()
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return FoodLogOut.from_orm(log)


@router.delete("/users/{target_user_id}/food-logs/{log_id}", status_code=204)
async def delete_food_log(
    target_user_id: str,
    log_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Supprimer un log alimentaire"""
    try:
        target_uuid = uuid.UUID(target_user_id)
        log_uuid = uuid.UUID(log_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="UUID invalide")

    log = db.query(FoodLog).filter(
        FoodLog.id == log_uuid,
        FoodLog.user_id == target_uuid
    ).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log alimentaire non trouvé")

    # TODO: Vérifier permissions (admin ou propriétaire)
    db.delete(log)
    db.commit()


# ─── ADMIN: All Food Logs ───

@router.get("/admin/food-logs", response_model=List[FoodLogOut])
async def get_all_food_logs(
    limit: int = Query(100, ge=1, le=1000),
    offset: int = Query(0, ge=0),
    user_id: str = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Admin: Récupérer tous les logs alimentaires (tous utilisateurs)"""
    logs = db.query(FoodLog).order_by(FoodLog.logged_at.desc()).offset(offset).limit(limit).all()
    return [FoodLogOut.from_orm(log) for log in logs]