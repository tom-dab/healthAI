"""Orchestrateur principal — cascade Cache → Ollama → HuggingFace → Fallback."""

from app.services import cache_service, ollama_service, huggingface_service, fallback_service

SYSTEM_ANALYZE = """Tu es un expert en nutrition.
Retourne UNIQUEMENT un JSON valide sans markdown ni texte avant/après.
Structure obligatoire :
{
  "aliments": [{"nom": "string", "quantite": "string", "calories": int}],
  "nutrition": {"calories": int, "proteines": float, "glucides": float, "lipides": float},
  "score_sante": int,
  "desequilibres": ["string"],
  "conseils": ["string"]
}"""

SYSTEM_MEAL_PLAN = """Tu es un diététicien expert.
Retourne UNIQUEMENT un JSON valide sans markdown ni texte avant/après.
Structure obligatoire :
{
  "plan": [
    {
      "jour": int,
      "petit_dejeuner": {"nom": "string", "calories": int, "ingredients": ["string"]},
      "dejeuner": {"nom": "string", "calories": int, "ingredients": ["string"]},
      "diner": {"nom": "string", "calories": int, "ingredients": ["string"]},
      "total_calories": int
    }
  ]
}"""

SYSTEM_ACTIVITY = """Tu es un coach sportif expert.
Retourne UNIQUEMENT un JSON valide sans markdown ni texte avant/après.
Structure obligatoire :
{
  "programme": [
    {
      "jour": int,
      "type_seance": "string",
      "exercices": [{"nom": "string", "series": int, "repetitions": "string", "repos_sec": int}],
      "duree_estimee_min": int
    }
  ],
  "conseils": ["string"]
}"""


async def analyze_nutrition(description: str, health_goal: str, image_bytes: bytes | None = None) -> dict:
    cache_key = cache_service.make_key("analyze", {"desc": description, "goal": health_goal})
    cached = cache_service.get(cache_key)
    if cached:
        return cached

    aliments_desc = description
    if image_bytes:
        try:
            labels = await huggingface_service.classify_image(image_bytes)
            aliments_desc = ", ".join(labels)
        except Exception:
            pass

    try:
        result = await ollama_service.generate(
            SYSTEM_ANALYZE,
            f"Analyse ce repas (objectif: {health_goal}): {aliments_desc}",
        )
        result["source"] = "ollama"
        cache_service.set(cache_key, result)
        return result
    except Exception:
        pass

    result = fallback_service.nutrition_analyze_fallback(aliments_desc)
    cache_service.set(cache_key, result)
    return result


async def generate_meal_plan(objectif: str, calories_cible: int, duree_jours: int,
                              budget: str | None, regime: str | None, allergies: list[str]) -> dict:
    cache_key = cache_service.make_key("meal_plan", {
        "objectif": objectif, "cal": calories_cible, "jours": duree_jours,
        "budget": budget, "regime": regime, "allergies": allergies,
    })
    cached = cache_service.get(cache_key)
    if cached:
        return cached

    user_msg = (
        f"Génère un plan de repas de {duree_jours} jours. "
        f"Objectif: {objectif}. Calories/jour: {calories_cible}. "
        f"Budget: {budget or 'moyen'}. Régime: {regime or 'aucun'}. "
        f"Allergies: {', '.join(allergies) if allergies else 'aucune'}."
    )
    try:
        result = await ollama_service.generate(SYSTEM_MEAL_PLAN, user_msg)
        result["source"] = "ollama"
        cache_service.set(cache_key, result)
        return result
    except Exception:
        result = fallback_service.meal_plan_fallback(objectif, duree_jours)
        cache_service.set(cache_key, result)
        return result


async def recommend_activity(objectif: str, niveau: str, duree_seance_min: int,
                              equipements: list[str], limitations: list[str]) -> dict:
    cache_key = cache_service.make_key("activity", {
        "objectif": objectif, "niveau": niveau, "duree": duree_seance_min,
        "equip": equipements, "limit": limitations,
    })
    cached = cache_service.get(cache_key)
    if cached:
        return cached

    user_msg = (
        f"Génère un programme d'entraînement. "
        f"Objectif: {objectif}. Niveau: {niveau}. "
        f"Durée séance: {duree_seance_min} min. "
        f"Équipements: {', '.join(equipements) if equipements else 'aucun'}. "
        f"Limitations: {', '.join(limitations) if limitations else 'aucune'}."
    )
    try:
        result = await ollama_service.generate(SYSTEM_ACTIVITY, user_msg)
        result["source"] = "ollama"
        cache_service.set(cache_key, result)
        return result
    except Exception:
        result = fallback_service.activity_recommend_fallback(niveau)
        cache_service.set(cache_key, result)
        return result
