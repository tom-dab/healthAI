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
from core.database import engine, Base

# Import des modèles (crucial pour que SQLAlchemy les crée)
from models.user import User  # noqa: F401
from models.nutrition import NutritionItem, FoodLog  # noqa: F401
from models.exercise import Exercise, WorkoutLog  # noqa: F401

# Import des routers
from routers import auth, users, nutrition, exercises, metrics

# ─────────────────────────────────────────────────────────────────
# Startup: Créer les tables à la première exécution
# ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gère le cycle de vie de l'application."""
    # Startup
    print("🚀 Démarrage HealthAI Coach API...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables créées (ou vérifiées)")
    
    # Créer admin par défaut si aucun admin n'existe
    db = SessionLocal()
    try:
        admin_exists = db.query(User).filter(User.role == "admin").first()
        if not admin_exists:
            from core.security import hash_password
            admin_user = User(
                email="admin@healthai.com",
                username="admin",
                password_hash=hash_password("admin123"),
                first_name="Admin",
                last_name="System",
                role="admin",
                plan="premium_plus"
            )
            db.add(admin_user)
            db.commit()
            print("✅ Admin par défaut créé: admin@healthai.com / admin123")
        else:
            print("✅ Admin déjà présent")
    except Exception as e:
        print(f"⚠️ Erreur création admin: {e}")
    finally:
        db.close()
    
    yield
    
    # Shutdown
    print("👋 Arrêt HealthAI Coach API...")


# ─────────────────────────────────────────────────────────────────
# Création de l'app FastAPI
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
# Configuration CORS
# ─────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────────
# Endpoints de santé
# ─────────────────────────────────────────────────────────────────
@app.get("/", tags=["health"])
def root():
    """Point de santé de l'API."""
    return {
        "status": "ok",
        "service": "HealthAI Coach API",
        "version": settings.api_version,
        "environment": settings.environment,
    }


@app.get("/health", tags=["health"])
def health_check():
    """Healthcheck pour Docker et CI."""
    return {
        "status": "healthy",
        "service": "HealthAI Coach API",
    }


# ─────────────────────────────────────────────────────────────────
# Inclusion des routers
# ─────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(nutrition.router)
app.include_router(exercises.router)
app.include_router(metrics.router)

# À ajouter ultérieurement:
# app.include_router(metrics.router)
