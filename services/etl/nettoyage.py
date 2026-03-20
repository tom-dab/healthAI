import pandas as pd
import os
from datetime import datetime

# ── Configuration ─────────────────────────────────────────
DATA_DIR   = r"C:\Users\houss\Desktop\healthai-coach\data\raw"
OUTPUT_DIR = r"C:\Users\houss\Desktop\healthai-coach\data\clean"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Chargement des données brutes ──────────────────────────
print("📥 Chargement des données brutes...\n")

food = pd.read_csv(os.path.join(DATA_DIR, "daily_food_nutrition_dataset.csv"), on_bad_lines='skip')
diet = pd.read_csv(os.path.join(DATA_DIR, "diet_recommendations_dataset.csv"))
gym  = pd.read_csv(os.path.join(DATA_DIR, "gym_members_exercise_tracking.csv"))
synt = pd.read_csv(os.path.join(DATA_DIR, "gym_members_exercise_tracking_synthetic_data.csv"))

# ══════════════════════════════════════════════════════════
# DATASET 1 — daily_food_nutrition
# ══════════════════════════════════════════════════════════
print("🧹 Nettoyage daily_food_nutrition...")

avant = len(food)
food = food.drop_duplicates()
print(f"   ✅ Doublons supprimés : {avant - len(food)}")
print(f"   ✅ Lignes restantes   : {len(food)}")

food.to_csv(os.path.join(OUTPUT_DIR, "daily_food_nutrition_clean.csv"), index=False)
print("   💾 Fichier sauvegardé : daily_food_nutrition_clean.csv\n")

# ══════════════════════════════════════════════════════════
# DATASET 2 — diet_recommendations
# ══════════════════════════════════════════════════════════
print("🧹 Nettoyage diet_recommendations...")

# Valeurs manquantes → remplacement par "Non renseigné"
avant_manq = diet.isnull().sum().sum()
diet["Disease_Type"]        = diet["Disease_Type"].fillna("Non renseigné")
diet["Dietary_Restrictions"] = diet["Dietary_Restrictions"].fillna("Non renseigné")
diet["Allergies"]            = diet["Allergies"].fillna("Non renseigné")
print(f"   ✅ Valeurs manquantes traitées : {avant_manq}")
print(f"   ✅ Lignes restantes : {len(diet)}")

diet.to_csv(os.path.join(OUTPUT_DIR, "diet_recommendations_clean.csv"), index=False)
print("   💾 Fichier sauvegardé : diet_recommendations_clean.csv\n")

# ══════════════════════════════════════════════════════════
# DATASET 3 — gym_members_exercise
# ══════════════════════════════════════════════════════════
print("🧹 Nettoyage gym_members_exercise...")

# Déjà propre mais on normalise les noms de colonnes
gym.columns = gym.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("(", "").str.replace(")", "")
print(f"   ✅ Colonnes normalisées")
print(f"   ✅ Lignes restantes : {len(gym)}")

gym.to_csv(os.path.join(OUTPUT_DIR, "gym_members_exercise_clean.csv"), index=False)
print("   💾 Fichier sauvegardé : gym_members_exercise_clean.csv\n")

# ══════════════════════════════════════════════════════════
# DATASET 4 — gym_members_synthetic
# ══════════════════════════════════════════════════════════
print("🧹 Nettoyage gym_members_synthetic...")

# Correction type Max_BPM str → numérique
synt["Max_BPM"] = pd.to_numeric(synt["Max_BPM"], errors='coerce')
print(f"   ✅ Colonne Max_BPM convertie en numérique")

# Valeurs manquantes → suppression des lignes incomplètes
avant = len(synt)
synt = synt.dropna()
print(f"   ✅ Lignes supprimées (trop de manquants) : {avant - len(synt)}")
print(f"   ✅ Lignes restantes : {len(synt)}")

# Normalisation colonnes
synt.columns = synt.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("(", "").str.replace(")", "")

synt.to_csv(os.path.join(OUTPUT_DIR, "gym_members_synthetic_clean.csv"), index=False)
print("   💾 Fichier sauvegardé : gym_members_synthetic_clean.csv\n")

# ══════════════════════════════════════════════════════════
# RÉSUMÉ FINAL
# ══════════════════════════════════════════════════════════
print("=" * 50)
print("✅ NETTOYAGE TERMINÉ")
print(f"📁 Fichiers propres dans : {OUTPUT_DIR}")
print("=" * 50)