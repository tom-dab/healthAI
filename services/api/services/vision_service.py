import base64
import logging
from typing import Optional
from uuid import UUID

import httpx
from sqlalchemy import text
from sqlalchemy.orm import Session

from core.config import settings
from schemas.meal_analysis import MealAnalysisResponse, NutritionSummary

logger = logging.getLogger(__name__)

_HUGGINGFACE_URL = "https://api-inference.huggingface.co/models/google/vit-base-patch16-224"
_GOOGLE_VISION_URL = "https://vision.googleapis.com/v1/images:annotate"

_RECOMMENDATIONS: dict[str, list[str]] = {
    "protein_deficit": [
        "Ajoutez une source de protéines : viande, poisson, légumineuses ou œufs.",
        "Visez 20-30 g de protéines par repas pour maintenir votre masse musculaire.",
    ],
    "carb_excess": [
        "Réduisez les glucides raffinés et privilégiez les céréales complètes.",
        "Équilibrez avec des légumes non féculents pour augmenter la satiété.",
    ],
    "fat_excess": [
        "Limitez les graisses saturées et privilégiez les graisses insaturées (huile d'olive, avocat).",
        "Réduisez les portions de fromages ou charcuteries si présents.",
    ],
    "balanced": [
        "Votre repas semble bien équilibré, continuez ainsi !",
        "Pensez à bien vous hydrater (1,5 à 2 L d'eau par jour).",
    ],
    "unknown": [
        "Nous n'avons pas pu analyser précisément ce repas.",
        "Essayez de varier vos sources de protéines, glucides et lipides.",
    ],
}


class VisionService:

    async def analyze_meal(
        self,
        image_bytes: bytes,
        filename: str,
        db: Session,
        analysis_id: UUID,
    ) -> MealAnalysisResponse:
        food_labels: list[str] = []
        source = "fallback_manual"
        confidence = 0.0
        is_fallback = False
        message: Optional[str] = None

        # 1. Tentative Hugging Face
        hf_result = await self._try_huggingface(image_bytes)
        if hf_result is not None:
            food_labels = hf_result["labels"]
            confidence = hf_result["confidence"]
            source = "huggingface"
            logger.info("Hugging Face OK — labels détectés : %s", food_labels)
        else:
            # 2. Tentative Google Vision
            logger.info("Hugging Face indisponible — tentative Google Vision")
            gv_result = await self._try_google_vision(image_bytes)
            if gv_result is not None:
                food_labels = gv_result["labels"]
                confidence = gv_result["confidence"]
                source = "google_vision"
                logger.info("Google Vision OK — labels détectés : %s", food_labels)
            else:
                # 3. Mode dégradé
                logger.warning("Les deux APIs sont indisponibles — mode fallback activé")
                source = "fallback_manual"
                is_fallback = True
                confidence = 0.0
                message = "Analyse automatique indisponible. Veuillez saisir manuellement."

        nutrition_data = self.calculate_nutrition(food_labels, db)
        balance = self._assess_balance(
            nutrition_data["calories"],
            nutrition_data["proteins_g"],
            nutrition_data["carbs_g"],
            nutrition_data["fats_g"],
        )
        recommendations = _RECOMMENDATIONS.get(balance, _RECOMMENDATIONS["unknown"])

        nutrition = NutritionSummary(
            calories=nutrition_data["calories"],
            proteins_g=nutrition_data["proteins_g"],
            carbs_g=nutrition_data["carbs_g"],
            fats_g=nutrition_data["fats_g"],
            is_estimated=nutrition_data["is_estimated"],
        )

        return MealAnalysisResponse(
            analysis_id=analysis_id,
            detected_foods=food_labels,
            nutrition=nutrition,
            balance=balance,
            recommendations=recommendations,
            confidence=confidence,
            source=source,
            is_fallback=is_fallback,
            message=message,
        )

    async def _try_huggingface(self, image_bytes: bytes) -> Optional[dict]:
        try:
            logger.info("Tentative Hugging Face (google/vit-base-patch16-224)")
            headers: dict[str, str] = {"Content-Type": "application/octet-stream"}
            if settings.huggingface_api_key:
                headers["Authorization"] = f"Bearer {settings.huggingface_api_key}"

            async with httpx.AsyncClient(timeout=8.0) as client:
                response = await client.post(_HUGGINGFACE_URL, content=image_bytes, headers=headers)

            if response.status_code != 200:
                logger.warning("Hugging Face — statut HTTP inattendu : %d", response.status_code)
                return None

            data = response.json()
            if not isinstance(data, list) or not data:
                logger.warning("Hugging Face — format de réponse inattendu")
                return None

            labels = [item["label"] for item in data[:5] if item.get("score", 0) > 0.05]
            top_score = float(data[0].get("score", 0.0)) if data else 0.0
            logger.info("Hugging Face succès — score max : %.3f", top_score)
            return {"labels": labels, "confidence": top_score}

        except httpx.TimeoutException:
            logger.warning("Hugging Face — timeout (8 s)")
            return None
        except httpx.ConnectError:
            logger.warning("Hugging Face — erreur de connexion")
            return None
        except Exception as exc:
            logger.warning("Hugging Face — erreur inattendue : %s", type(exc).__name__)
            return None

    async def _try_google_vision(self, image_bytes: bytes) -> Optional[dict]:
        if not settings.google_vision_api_key:
            logger.warning("Google Vision — clé API absente, étape ignorée")
            return None

        try:
            logger.info("Tentative Google Vision API")
            image_b64 = base64.b64encode(image_bytes).decode("utf-8")
            payload = {
                "requests": [
                    {
                        "image": {"content": image_b64},
                        "features": [
                            {"type": "LABEL_DETECTION", "maxResults": 10},
                            {"type": "WEB_DETECTION", "maxResults": 5},
                        ],
                    }
                ]
            }

            # La clé API est passée en query param, jamais dans les logs
            url = f"{_GOOGLE_VISION_URL}?key={settings.google_vision_api_key}"
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(url, json=payload)

            if response.status_code != 200:
                logger.warning("Google Vision — statut HTTP inattendu : %d", response.status_code)
                return None

            data = response.json()
            first = (data.get("responses") or [{}])[0]
            label_annotations = first.get("labelAnnotations", [])

            labels: list[str] = []
            for ann in label_annotations[:8]:
                desc = ann.get("description", "")
                if ann.get("score", 0.0) > 0.5 and desc:
                    labels.append(desc)

            for entity in first.get("webDetection", {}).get("webEntities", [])[:3]:
                desc = entity.get("description", "")
                if entity.get("score", 0.0) > 0.5 and desc and desc not in labels:
                    labels.append(desc)

            confidence = float(label_annotations[0].get("score", 0.0)) if label_annotations else 0.0
            logger.info("Google Vision succès — score max : %.3f", confidence)
            return {"labels": labels[:8], "confidence": confidence}

        except httpx.TimeoutException:
            logger.warning("Google Vision — timeout (10 s)")
            return None
        except httpx.ConnectError:
            logger.warning("Google Vision — erreur de connexion")
            return None
        except Exception as exc:
            logger.warning("Google Vision — erreur inattendue : %s", type(exc).__name__)
            return None

    def calculate_nutrition(self, food_labels: list[str], db: Session) -> dict:
        _empty = {"calories": 0.0, "proteins_g": 0.0, "carbs_g": 0.0, "fats_g": 0.0, "is_estimated": True}

        if not food_labels:
            return _empty

        try:
            conditions = " OR ".join(f"LOWER(name) LIKE :lbl_{i}" for i in range(len(food_labels)))
            params = {f"lbl_{i}": f"%{label.lower()}%" for i, label in enumerate(food_labels)}

            row = db.execute(
                text(
                    f"""
                    SELECT
                        COALESCE(SUM(CAST(calories   AS float)), 0),
                        COALESCE(SUM(CAST(proteins_g AS float)), 0),
                        COALESCE(SUM(CAST(carbs_g    AS float)), 0),
                        COALESCE(SUM(CAST(fats_g     AS float)), 0),
                        COUNT(*)
                    FROM nutrition_items
                    WHERE {conditions}
                    """
                ),
                params,
            ).fetchone()

            if row and int(row[4]) > 0:
                return {
                    "calories": round(float(row[0]), 1),
                    "proteins_g": round(float(row[1]), 1),
                    "carbs_g": round(float(row[2]), 1),
                    "fats_g": round(float(row[3]), 1),
                    "is_estimated": False,
                }

            logger.info("Aucun aliment trouvé en base pour les labels : %s", food_labels)
        except Exception as exc:
            logger.warning("calculate_nutrition — erreur SQL : %s", type(exc).__name__)

        return _empty

    @staticmethod
    def _assess_balance(calories: float, proteins_g: float, carbs_g: float, fats_g: float) -> str:
        if calories == 0.0:
            return "unknown"

        total = proteins_g + carbs_g + fats_g
        if total == 0.0:
            return "unknown"

        if proteins_g / total < 0.15:
            return "protein_deficit"
        if carbs_g / total > 0.65:
            return "carb_excess"
        if fats_g / total > 0.40:
            return "fat_excess"
        return "balanced"
