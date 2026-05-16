import logging
import time
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Request, Response, UploadFile, status
from sqlalchemy.orm import Session

from core.database import get_db
from models.meal_analysis import MealAnalysis
from schemas.meal_analysis import MealAnalysisResponse, NutritionSummary
from services.vision_service import VisionService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vision", tags=["Vision / Meal Analysis"])

_ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
_MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
_RATE_LIMIT = 10  # appels par heure par IP

# {ip: [unix_timestamps]}
_rate_limit_store: dict[str, list[float]] = {}

_vision_service = VisionService()


def _check_rate_limit(ip: str) -> int:
    """Retourne le nombre d'appels restants pour cette heure. Lève 429 si dépassé."""
    now = time.time()
    window = 3600.0
    calls = [t for t in _rate_limit_store.get(ip, []) if now - t < window]
    _rate_limit_store[ip] = calls

    if len(calls) >= _RATE_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit dépassé : maximum 10 analyses par heure par IP.",
        )

    _rate_limit_store[ip].append(now)
    return _RATE_LIMIT - len(_rate_limit_store[ip])


@router.post(
    "/analyze-meal",
    response_model=MealAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyse nutritionnelle d'une photo de repas",
)
async def analyze_meal(
    request: Request,
    response: Response,
    file: UploadFile = File(..., description="Image du repas (jpeg/png/webp, max 5 MB)"),
    db: Session = Depends(get_db),
) -> MealAnalysisResponse:
    client_ip = request.client.host if request.client else "unknown"
    remaining = _check_rate_limit(client_ip)
    response.headers["X-RateLimit-Remaining"] = str(remaining)

    if file.content_type not in _ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Type de fichier non supporté : '{file.content_type}'. Acceptés : image/jpeg, image/png, image/webp.",
        )

    image_bytes = await file.read()

    if len(image_bytes) > _MAX_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fichier trop volumineux. Taille maximale : 5 MB.",
        )

    analysis_id = uuid4()
    safe_filename = file.filename or "upload.jpg"
    logger.info("Analyse repas [%s] démarrée — IP : %s — fichier : %s", analysis_id, client_ip, safe_filename)

    result = await _vision_service.analyze_meal(
        image_bytes=image_bytes,
        filename=safe_filename,
        db=db,
        analysis_id=analysis_id,
    )

    record = MealAnalysis(
        id=analysis_id,
        image_filename=safe_filename,
        vision_source=result.source,
        detected_foods=result.detected_foods,
        calories_estimated=result.nutrition.calories,
        proteins_g=result.nutrition.proteins_g,
        carbs_g=result.nutrition.carbs_g,
        fats_g=result.nutrition.fats_g,
        nutritional_balance=result.balance,
        recommendations=result.recommendations,
        confidence_score=result.confidence,
        is_fallback=result.is_fallback,
    )
    db.add(record)
    db.commit()

    logger.info("Analyse repas [%s] sauvegardée — source : %s — balance : %s", analysis_id, result.source, result.balance)
    return result


@router.get(
    "/analyze-meal/{analysis_id}",
    response_model=MealAnalysisResponse,
    summary="Récupère une analyse sauvegardée par son identifiant",
)
async def get_meal_analysis(
    analysis_id: UUID,
    db: Session = Depends(get_db),
) -> MealAnalysisResponse:
    record: MealAnalysis | None = (
        db.query(MealAnalysis).filter(MealAnalysis.id == analysis_id).first()
    )
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analyse '{analysis_id}' introuvable.",
        )

    nutrition = NutritionSummary(
        calories=record.calories_estimated or 0.0,
        proteins_g=record.proteins_g or 0.0,
        carbs_g=record.carbs_g or 0.0,
        fats_g=record.fats_g or 0.0,
        is_estimated=record.is_fallback or (record.calories_estimated == 0.0),
    )

    return MealAnalysisResponse(
        analysis_id=record.id,
        detected_foods=record.detected_foods or [],
        nutrition=nutrition,
        balance=record.nutritional_balance,
        recommendations=record.recommendations or [],
        confidence=record.confidence_score,
        source=record.vision_source,
        is_fallback=record.is_fallback,
        message=(
            "Analyse automatique indisponible. Veuillez saisir manuellement."
            if record.is_fallback
            else None
        ),
    )
