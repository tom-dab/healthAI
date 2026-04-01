"""
HealthAI Coach — Authentication Router
Endpoints pour login, register, logout et profil utilisateur
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..core.security import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
)
from ..models.user import User
from ..schemas.user import (
    UserCreate,
    LoginRequest,
    TokenResponse,
    UserOut,
    ProfileResponse,
)

router = APIRouter(prefix="/auth", tags=["authentication"])


# ─────────────────────────────────────────────────────────────────
# POST /auth/register
# ─────────────────────────────────────────────────────────────────
@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Créer un nouvel utilisateur",
    responses={
        400: {"description": "Utilisateur existe déjà / données invalides"},
        500: {"description": "Erreur serveur"},
    }
)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Enregistre un nouvel utilisateur.
    
    - **email**: Adresse email unique
    - **username**: Nom d'utilisateur (3-100 caractères)
    - **password**: Mot de passe (min 8 caractères)
    - **age**: Âge optionnel (1-120)
    - **gender**: Genre optionnel (male/female/other)
    - **height_cm**: Hauteur optionnelle en cm
    - **weight_kg**: Poids optionnel en kg
    - **goal**: Objectif personnel
    - **plan**: Plan d'abonnement
    
    Retourne un JWT token et les données utilisateur.
    """
    # Vérifier que l'email n'existe pas
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cet email est déjà utilisé",
        )
    
    # Vérifier que l'username n'existe pas
    existing_username = db.query(User).filter(
        User.username == user_data.username
    ).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce nom d'utilisateur est déjà pris",
        )
    
    # Créer nouvel utilisateur
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
    
    # Créer JWT token
    access_token = create_access_token(data={"sub": str(db_user.id)})
    
    return TokenResponse(
        access_token=access_token,
        user=UserOut.from_orm(db_user),
    )


# ─────────────────────────────────────────────────────────────────
# POST /auth/login
# ─────────────────────────────────────────────────────────────────
@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Connexion utilisateur",
    responses={
        400: {"description": "Email ou mot de passe incorrect"},
        401: {"description": "Authentification échouée"},
    }
)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Authentifie un utilisateur avec email et mot de passe.
    
    - **email**: Adresse email
    - **password**: Mot de passe
    
    Retourne un JWT token valide pour 24h.
    """
    # Chercher l'utilisateur par email
    db_user = db.query(User).filter(User.email == credentials.email).first()
    
    if not db_user or not verify_password(credentials.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Créer JWT token
    access_token = create_access_token(data={"sub": str(db_user.id)})
    
    return TokenResponse(
        access_token=access_token,
        user=UserOut.from_orm(db_user),
    )


# ─────────────────────────────────────────────────────────────────
# GET /auth/profile
# ─────────────────────────────────────────────────────────────────
@router.get(
    "/profile",
    response_model=ProfileResponse,
    summary="Récupérer le profil de l'utilisateur connecté",
    responses={
        401: {"description": "Non authentifié"},
        404: {"description": "Utilisateur non trouvé"},
    }
)
async def get_profile(
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Récupère le profil de l'utilisateur connecté.
    Nécessite un JWT token valide en header Authorization.
    
    Retourne les données complètes de l'utilisateur.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé",
        )
    
    return ProfileResponse(user=UserOut.from_orm(db_user))


# ─────────────────────────────────────────────────────────────────
# PUT /auth/profile
# ─────────────────────────────────────────────────────────────────
@router.put(
    "/profile",
    response_model=ProfileResponse,
    summary="Mettre à jour le profil de l'utilisateur connecté",
    responses={
        400: {"description": "Données invalides"},
        401: {"description": "Non authentifié"},
        404: {"description": "Utilisateur non trouvé"},
    }
)
async def update_profile(
    user_update: dict,  # Flexible pour ne modifier que ce qui est fourni
    user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Met à jour le profil de l'utilisateur connecté.
    Ne modifie que les champs fournis (PATCH behavior).
    
    Les champs modifiables:
    - username, age, gender, height_cm, weight_kg, goal, plan
    
    Note: email ne peut pas être changé en PUT (sécurité)
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Utilisateur non trouvé",
        )
    
    # Champs modifiables
    allowed_fields = {"username", "age", "gender", "height_cm", "weight_kg", "goal", "plan"}
    
    for field, value in user_update.items():
        if field in allowed_fields and value is not None:
            setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    
    return ProfileResponse(user=UserOut.from_orm(db_user))


# ─────────────────────────────────────────────────────────────────
# POST /auth/logout
# ─────────────────────────────────────────────────────────────────
@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Déconnexion utilisateur",
)
async def logout(user_id: str = Depends(get_current_user)):
    """
    Termine la session utilisateur.
    
    Note: Avec JWT, le logout est principalement côté client
    (suppression du token du localStorage). Cet endpoint existe
    pour validité API et logging serveur.
    """
    # En production, on pourrait invalider le token côté serveur
    # ou logger la déconnexion
    return None
