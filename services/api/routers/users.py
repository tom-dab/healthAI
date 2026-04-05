"""
HealthAI Coach — Users CRUD Router
Endpoints pour gérer les utilisateurs (admin)
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
import uuid

from core.database import get_db
from core.security import get_current_user, hash_password, get_current_admin_user
from models.user import User
from schemas.user import UserCreate, UserUpdate, UserOut, UserListResponse

router = APIRouter(prefix="/api/v1/users", tags=["users"])


# ─────────────────────────────────────────────────────────────────
# GET /api/v1/users
# ─────────────────────────────────────────────────────────────────
@router.get(
    "",
    response_model=UserListResponse,
    summary="Lister tous les utilisateurs",
    responses={
        401: {"description": "Non authentifié"},
    }
)
async def list_users(
    limit: int = Query(10, ge=1, le=100, description="Nombre max de résultats"),
    offset: int = Query(0, ge=0, description="Offset pour pagination"),
    goal: str = Query(None, description="Filtrer par objectif (optionnel)"),
    plan: str = Query(None, description="Filtrer par plan (optionnel)"),
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Liste tous les utilisateurs avec pagination et filtres optionnels.
    
    **Query Parameters:**
    - `limit`: Nombre max de résultats (1-100, défaut: 10)
    - `offset`: Décalage pour pagination (défaut: 0)
    - `goal`: Filtrer par objectif (weight_loss, muscle_gain, etc.)
    - `plan`: Filtrer par plan (free, premium, premium_plus)
    
    Retourne une liste paginée d'utilisateurs.
    """
    query = db.query(User)
    
    # Appliquer les filtres
    if goal:
        query = query.filter(User.goal == goal)
    if plan:
        query = query.filter(User.plan == plan)
    
    # Compter total avant pagination
    total = query.count()
    
    # Appliquer pagination
    items = query.offset(offset).limit(limit).all()
    
    return UserListResponse(
        total=total,
        limit=limit,
        offset=offset,
        items=[UserOut.from_orm(u) for u in items],
    )


# ─────────────────────────────────────────────────────────────────
# GET /api/v1/users/{user_id}
# ─────────────────────────────────────────────────────────────────
@router.get(
    "/{target_user_id}",
    response_model=UserOut,
    summary="Récupérer un utilisateur par son ID",
    responses={
        401: {"description": "Non authentifié"},
        404: {"description": "Utilisateur non trouvé"},
    }
)
async def get_user(
    target_user_id: str,
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Récupère les détails d'un utilisateur spécifique par son UUID.
    """
    # Parser le UUID
    try:
        target_uuid = uuid.UUID(target_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format UUID invalide",
        )
    
    db_user = db.query(User).filter(User.id == target_uuid).first()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé",
        )
    
    return UserOut.from_orm(db_user)


# ─────────────────────────────────────────────────────────────────
# POST /api/v1/users (Admin creation)
# ─────────────────────────────────────────────────────────────────
@router.post(
    "",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un nouvel utilisateur (Admin)",
    responses={
        400: {"description": "Email/username existe déjà"},
        401: {"description": "Non authentifié"},
    }
)
async def create_user(
    user_data: UserCreate,
    user_id: str = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Crée un nouvel utilisateur (endpoint admin).
    
    **Paramètres:**
    - `email`: Adresse email unique
    - `username`: Nom d'utilisateur unique (3-100 caractères)
    - `password`: Mot de passe (min 8 caractères)
    - `age`: Âge optionnel
    - `gender`: Genre optionnel (male/female/other)
    - etc.
    
    Retourne l'utilisateur créé avec son UUID.
    """
    # Vérifier email unique
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet email est déjà utilisé",
        )
    
    # Vérifier username unique
    existing_username = db.query(User).filter(
        User.username == user_data.username
    ).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce nom d'utilisateur est déjà pris",
        )
    
    # Créer utilisateur
    db_user = User(
        email=user_data.email,
        username=user_data.username,
        password_hash=hash_password(user_data.password),
        age=user_data.age,
        gender=user_data.gender,
        height_cm=user_data.height_cm,
        weight_kg=user_data.weight_kg,
        goal=user_data.goal,
        plan=user_data.plan,
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return UserOut.from_orm(db_user)


# ─────────────────────────────────────────────────────────────────
# PUT /api/v1/users/{user_id}
# ─────────────────────────────────────────────────────────────────
@router.put(
    "/{target_user_id}",
    response_model=UserOut,
    summary="Mettre à jour un utilisateur",
    responses={
        400: {"description": "Données invalides / email doublé"},
        401: {"description": "Non authentifié"},
        404: {"description": "Utilisateur non trouvé"},
    }
)
async def update_user(
    target_user_id: str,
    user_update: UserUpdate,
    user_id: str = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Met à jour les informations d'un utilisateur.
    
    Champs modifiables:
    - `email`, `username`, `age`, `gender`, `height_cm`, `weight_kg`, `goal`, `plan`
    
    Retourne l'utilisateur mis à jour.
    """
    try:
        target_uuid = uuid.UUID(target_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format UUID invalide",
        )
    
    db_user = db.query(User).filter(User.id == target_uuid).first()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé",
        )
    
    # Si email est modifié, vérifier l'unicité
    if user_update.email and user_update.email != db_user.email:
        existing = db.query(User).filter(User.email == user_update.email).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cet email est déjà utilisé",
            )
    
    # Mettre à jour les champs fournis
    update_data = user_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None:
            setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    
    return UserOut.from_orm(db_user)


# ─────────────────────────────────────────────────────────────────
# DELETE /api/v1/users/{user_id}
# ─────────────────────────────────────────────────────────────────
@router.delete(
    "/{target_user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Supprimer un utilisateur",
    responses={
        401: {"description": "Non authentifié"},
        404: {"description": "Utilisateur non trouvé"},
    }
)
async def delete_user(
    target_user_id: str,
    user_id: str = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Supprime un utilisateur (admin only).
    
    **WARNING:** Cette action est permanente.
    """
    try:
        target_uuid = uuid.UUID(target_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format UUID invalide",
        )
    
    db_user = db.query(User).filter(User.id == target_uuid).first()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé",
        )
    
    db.delete(db_user)
    db.commit()
    
    return None


# ─────────────────────────────────────────────────────────────────
# ADMIN: Promote User to Admin
# ─────────────────────────────────────────────────────────────────
@router.post(
    "/{target_user_id}/promote",
    response_model=UserOut,
    summary="Promouvoir un utilisateur en admin",
    responses={
        401: {"description": "Non authentifié"},
        403: {"description": "Non admin"},
        404: {"description": "Utilisateur non trouvé"},
    }
)
async def promote_user_to_admin(
    target_user_id: str,
    user_id: str = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Promouvoir un utilisateur au rôle admin.
    
    **Seul un admin peut promouvoir un autre utilisateur.**
    """
    try:
        target_uuid = uuid.UUID(target_user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format UUID invalide",
        )
    
    db_user = db.query(User).filter(User.id == target_uuid).first()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé",
        )
    
    # Promouvoir l'utilisateur
    db_user.role = "admin"
    db.commit()
    db.refresh(db_user)
    
    return UserOut.from_orm(db_user)
