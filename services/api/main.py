"""
HealthAI Coach — API REST
Responsable : Tojo

Point d'entrée principal de l'application FastAPI.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="HealthAI Coach API",
    description="API REST pour la plateforme HealthAI Coach — MSPR TPRE501",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configuration CORS (à restreindre en production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["health"])
def root():
    """Point de santé de l'API."""
    return {"status": "ok", "service": "HealthAI Coach API", "version": "0.1.0"}


@app.get("/health", tags=["health"])
def health_check():
    """Healthcheck pour Docker et CI."""
    return {"status": "healthy"}


# ─── Import des routers (Tojo : à compléter) ─────
# from routers import users, nutrition, exercises, metrics
# app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
# app.include_router(nutrition.router, prefix="/api/v1/nutrition", tags=["nutrition"])
# app.include_router(exercises.router, prefix="/api/v1/exercises", tags=["exercises"])
# app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["metrics"])
