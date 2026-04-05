import sys
import os
from loguru import logger
from datetime import datetime

# ── Configuration logs ─────────────────────────────────────
RAPPORT_DIR = r"C:\Users\houss\Desktop\healthai\healthAI\services\etl\rapport"
os.makedirs(RAPPORT_DIR, exist_ok=True)

logger.remove()
logger.add(sys.stdout, level="INFO", colorize=True)
logger.add(
    os.path.join(RAPPORT_DIR, "pipeline.log"),
    level="INFO",
    rotation="1 MB",
    encoding="utf-8"
)

# ── Pipeline ───────────────────────────────────────────────
def run_pipeline():
    debut = datetime.now()
    logger.info("=" * 50)
    logger.info("=== Démarrage du pipeline ETL HealthAI Coach ===")
    logger.info(f"Heure de démarrage : {debut.strftime('%d/%m/%Y à %H:%M:%S')}")
    logger.info("=" * 50)

    # ── Étape 1 : Extract ──────────────────────────────────
    logger.info("Étape 1/3 : Extraction et inventaire des données")
    try:
        import ingestion
        logger.success("✅ Extraction terminée — rapport_inventaire.md généré")
    except Exception as e:
        logger.error(f"❌ Extraction échouée : {e}")
        sys.exit(1)

    # ── Étape 2 : Transform ────────────────────────────────
    logger.info("Étape 2/3 : Nettoyage et transformation")
    try:
        import nettoyage_v2
        logger.success("✅ Nettoyage terminé — BDD + ML séparés, rapport_nettoyage_v2.md généré")
    except Exception as e:
        logger.error(f"❌ Nettoyage échoué : {e}")
        sys.exit(1)

    # ── Étape 3 : Load ─────────────────────────────────────
    logger.info("Étape 3/3 : Chargement BDD")
    logger.warning("⏳ En attente — intégration BDD gérée par l'équipe backend")

    # ── Bilan ──────────────────────────────────────────────
    fin = datetime.now()
    duree = (fin - debut).seconds
    logger.info("=" * 50)
    logger.success(f"✅ Pipeline ETL terminé en {duree} secondes")
    logger.info(f"Rapports disponibles dans : {RAPPORT_DIR}")
    logger.info("=" * 50)

if __name__ == "__main__":
    run_pipeline()