import os
import sys
from loguru import logger

logger.remove()
logger.add(sys.stdout, level="INFO")

def run_pipeline():
    logger.info("=== Démarrage du pipeline ETL HealthAI Coach ===")

    # ── Étape 1 : Extract ──────────────────────────
    logger.info("Étape 1/3 : Extraction des données")
    import ingestion
    logger.success("✅ Extraction terminée")

    # ── Étape 2 : Transform ───────────────────────
    logger.info("Étape 2/3 : Nettoyage et transformation")
    import nettoyage
    logger.success("✅ Nettoyage terminé")

    # ── Étape 3 : Load ────────────────────────────
    logger.info("Étape 3/3 : Chargement BDD (partie collègue)")
    logger.warning("⏳ En attente — partie BDD non encore intégrée")

    logger.success("=== Pipeline ETL terminé avec succès ===")

if __name__ == "__main__":
    run_pipeline()