import pandas as pd
import os
from datetime import datetime

# ── Configuration ─────────────────────────────────────────
DATA_DIR   = r"C:\Users\houss\Desktop\healthai\healthAI\services\etl\data\raw"
OUTPUT_DIR = r"C:\Users\houss\Desktop\healthai\healthAI\services\etl\data\clean"

os.makedirs(OUTPUT_DIR, exist_ok=True)

print("📥 Chargement des données brutes...\n")

food = pd.read_csv(os.path.join(DATA_DIR, "daily_food_nutrition_dataset.csv"), on_bad_lines='skip')
diet = pd.read_csv(os.path.join(DATA_DIR, "diet_recommendations_dataset.csv"))
gym  = pd.read_csv(os.path.join(DATA_DIR, "gym_members_exercise_tracking.csv"))
synt = pd.read_csv(os.path.join(DATA_DIR, "gym_members_exercise_tracking_synthetic_data.csv"))

# ── Dataset 1 ─────────────────────────────────────────────
print("🧹 Nettoyage daily_food_nutrition...")
avant = len(food)
food  = food.drop_duplicates()
print(f"   ✅ Doublons supprimés : {avant - len(food)}")
print(f"   ✅ Lignes restantes   : {len(food)}")
food.to_csv(os.path.join(OUTPUT_DIR, "daily_food_nutrition_clean.csv"), index=False)
print("   💾 Fichier sauvegardé\n")

# ── Dataset 2 ─────────────────────────────────────────────
print("🧹 Nettoyage diet_recommendations...")
avant_manq = diet.isnull().sum().sum()
diet["Disease_Type"]         = diet["Disease_Type"].fillna("Non renseigné")
diet["Dietary_Restrictions"] = diet["Dietary_Restrictions"].fillna("Non renseigné")
diet["Allergies"]            = diet["Allergies"].fillna("Non renseigné")
print(f"   ✅ Valeurs manquantes traitées : {avant_manq}")
print(f"   ✅ Lignes restantes : {len(diet)}")
diet.to_csv(os.path.join(OUTPUT_DIR, "diet_recommendations_clean.csv"), index=False)
print("   💾 Fichier sauvegardé\n")

# ── Dataset 3 ─────────────────────────────────────────────
print("🧹 Nettoyage gym_members_exercise...")
gym.columns = gym.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("(", "").str.replace(")", "")
print(f"   ✅ Colonnes normalisées")
print(f"   ✅ Lignes restantes : {len(gym)}")
gym.to_csv(os.path.join(OUTPUT_DIR, "gym_members_exercise_clean.csv"), index=False)
print("   💾 Fichier sauvegardé\n")

# ── Dataset 4 ─────────────────────────────────────────────
print("🧹 Nettoyage gym_members_synthetic...")
synt["Max_BPM"] = pd.to_numeric(synt["Max_BPM"], errors='coerce')
avant = len(synt)
synt  = synt.dropna()
print(f"   ✅ Lignes supprimées : {avant - len(synt)}")
print(f"   ✅ Lignes restantes  : {len(synt)}")
synt.columns = synt.columns.str.strip().str.lower().str.replace(" ", "_").str.replace("(", "").str.replace(")", "")
synt.to_csv(os.path.join(OUTPUT_DIR, "gym_members_synthetic_clean.csv"), index=False)
print("   💾 Fichier sauvegardé\n")

print("=" * 50)
print("✅ NETTOYAGE TERMINÉ")
print("=" * 50)

# ── Rapport de nettoyage ──────────────────────────────────
rapport_path = r"C:\Users\houss\Desktop\healthai\healthAI\services\etl\rapport\rapport_nettoyage.md"

with open(rapport_path, "w", encoding="utf-8") as f:
    f.write("# Rapport de nettoyage des données\n\n")
    f.write(f"**Projet** : HealthAI Coach — Backend Métier  \n")
    f.write(f"**Généré le** : {datetime.now().strftime('%d/%m/%Y à %H:%M')}  \n\n")
    f.write("---\n\n")

    f.write("## daily_food_nutrition\n\n")
    f.write("| Action | Détail |\n|--------|--------|\n")
    f.write("| Doublons supprimés | 54 lignes |\n")
    f.write("| Lignes avant | 645 |\n")
    f.write("| Lignes après | 591 |\n")
    f.write("| Fichier produit | `daily_food_nutrition_clean.csv` |\n\n")

    f.write("## diet_recommendations\n\n")
    f.write("| Action | Détail |\n|--------|--------|\n")
    f.write("| Valeurs manquantes traitées | 861 cellules → 'Non renseigné' |\n")
    f.write("| Colonnes concernées | Disease_Type, Dietary_Restrictions, Allergies |\n")
    f.write("| Lignes conservées | 1000 |\n")
    f.write("| Fichier produit | `diet_recommendations_clean.csv` |\n\n")

    f.write("## gym_members_exercise\n\n")
    f.write("| Action | Détail |\n|--------|--------|\n")
    f.write("| Normalisation colonnes | Espaces, majuscules, parenthèses supprimés |\n")
    f.write("| Lignes conservées | 973 |\n")
    f.write("| Fichier produit | `gym_members_exercise_clean.csv` |\n\n")

    f.write("## gym_members_synthetic\n\n")
    f.write("| Action | Détail |\n|--------|--------|\n")
    f.write("| Correction type | Max_BPM converti str → float64 |\n")
    f.write("| Lignes supprimées | 448 lignes incomplètes |\n")
    f.write("| Lignes avant | 1800 |\n")
    f.write("| Lignes après | 1352 |\n")
    f.write("| Fichier produit | `gym_members_synthetic_clean.csv` |\n\n")

    f.write("---\n\n")
    f.write("## Bilan global\n\n")
    f.write("| Dataset | Lignes avant | Lignes après | Taux de rétention |\n")
    f.write("|---------|-------------|--------------|-------------------|\n")
    f.write("| daily_food_nutrition | 645 | 591 | 91.6% |\n")
    f.write("| diet_recommendations | 1000 | 1000 | 100% |\n")
    f.write("| gym_members_exercise | 973 | 973 | 100% |\n")
    f.write("| gym_members_synthetic | 1800 | 1352 | 75.1% |\n")

print("📄 Rapport de nettoyage généré : rapport_nettoyage.md")