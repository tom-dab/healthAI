"""
HealthAI Coach — Pipeline ETL Principal
Responsable : Houssem

Orchestre l'ensemble de la chaîne ETL :
  Extract  → Chargement des datasets sources
  Transform → Nettoyage, normalisation, enrichissement
  Load     → Insertion en base PostgreSQL
"""
import os
import sys
from pathlib import Path
from loguru import logger

# ─── Configuration du logger ─────────────────────
logger.remove()
logger.add(sys.stdout, level=os.getenv("LOG_LEVEL", "INFO"))
logger.add("logs/etl_{time}.log", rotation="1 day", retention="7 days")


def run_pipeline():
    """Point d'entrée principal du pipeline ETL."""
    logger.info("=== Démarrage du pipeline ETL HealthAI Coach ===")

    # ── Étape 1 : Extract ──────────────────────────
    logger.info("Étape 1/3 : Extraction des données")
    # TODO (Houssem) : importer les extracteurs
    # from pipelines.extract import nutrition_extractor, users_extractor
    # nutrition_data = nutrition_extractor.run()
    # users_data = users_extractor.run()

    # ── Étape 2 : Transform ───────────────────────
    logger.info("Étape 2/3 : Nettoyage et transformation")
    # TODO (Houssem) : importer les transformateurs
    # from pipelines.transform import nutrition_transformer, users_transformer
    # clean_nutrition = nutrition_transformer.run(nutrition_data)
    # clean_users = users_transformer.run(users_data)

    # ── Étape 3 : Load ────────────────────────────
    logger.info("Étape 3/3 : Chargement en base de données")
    # TODO (Houssem) : importer les loaders
    # from pipelines.load import db_loader
    # db_loader.load(clean_nutrition, table="nutrition_items")
    # db_loader.load(clean_users, table="users")

    logger.success("=== Pipeline ETL terminé avec succès ===")


if __name__ == "__main__":
    run_pipeline()
