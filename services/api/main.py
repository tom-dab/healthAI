"""
HealthAI Coach — API REST
Responsable : Tojo

Point d'entrée principal de l'application FastAPI.
Intègre tous les routers et crée les tables à la première exécution.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import des configurations
from core.config import settings
from core.database import engine, Base, SessionLocal  # ← SessionLocal ajouté
from core.security import hash_password

# Import des modèles (crucial pour que SQLAlchemy les découvre et crée les tables)
from models.user import User          # noqa: F401
from models.nutrition import NutritionItem, FoodLog   # noqa: F401
from models.exercise import Exercise, WorkoutLog       # noqa: F401

# Import des routers
from routers import auth, users, nutrition, exercises, metrics


# ─────────────────────────────────────────────────────────────────
# Lifespan : startup + shutdown
# ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gère le cycle de vie de l'application."""
    print("🚀 Démarrage HealthAI Coach API...")

    # Créer les tables si elles n'existent pas encore
    # (sécurité : la migration SQL du container postgres prend la priorité)
    Base.metadata.create_all(bind=engine)
    print("✅ Tables vérifiées")

    # Créer l'utilisateur admin par défaut s'il n'existe pas
    db = SessionLocal()
    try:
        admin_exists = db.query(User).filter(User.role == "admin").first()
        if not admin_exists:
            admin_user = User(
                email="admin@healthai.com",
                username="admin",
                password_hash=hash_password("admin123"),
                role="admin",
                plan="premium_plus",
                goal="general_health",
            )
            db.add(admin_user)
            db.commit()
            print("✅ Admin créé : admin@healthai.com / admin123")
        else:
            print("✅ Admin déjà présent")
    except Exception as e:
        print(f"⚠️  Erreur création admin : {e}")
        db.rollback()
    finally:
        db.close()

    yield

    print("👋 Arrêt HealthAI Coach API...")


# ─────────────────────────────────────────────────────────────────
# Application FastAPI
# ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ─────────────────────────────────────────────────────────────────
# CORS
# ─────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────────
# Endpoints de santé (pas d'auth requis)
# ─────────────────────────────────────────────────────────────────
@app.get("/", tags=["health"])
def root():
    """Point d'entrée racine."""
    return {
        "status": "ok",
        "service": "HealthAI Coach API",
        "version": settings.api_version,
        "environment": settings.environment,
        "docs": "/docs",
    }


@app.get("/health", tags=["health"])
def health_check():
    """Healthcheck pour Docker et CI/CD."""
    return {
        "status": "healthy",
        "service": "HealthAI Coach API",
    }


# ─────────────────────────────────────────────────────────────────
# Routers
# ─────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(nutrition.router)
app.include_router(exercises.router)
app.include_router(metrics.router)
